# agents/agentA_knowledge/graph.py

from langchain_core.pydantic_v1 import BaseModel, Field
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
import operator
import tempfile
import os

# Import our new tools
from tools import download_file_from_drive, get_chroma_client

# Import LangChain components
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

# --- State Definition (Ingestion) ---
class IngestionState(TypedDict):
    driveFileId: str
    doc_chunks: List
    num_chunks: int

# --- Node Definitions (Ingestion - These remain synchronous) ---
def download_and_load(state: IngestionState) -> IngestionState:
    print("--- Entering Node: download_and_load ---")
    file_id = state['driveFileId']
    documents = []
    file_buffer = download_file_from_drive(file_id)
    if file_buffer is None:
        return {"doc_chunks": [], "num_chunks": 0}
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_buffer.getvalue())
            temp_file_path = temp_file.name
        if file_buffer.mimeType == 'application/pdf':
            loader = PyPDFLoader(temp_file_path)
            documents = loader.load()
    finally:
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
    for doc in documents:
        doc.metadata["source"] = file_buffer.name
    return {"doc_chunks": documents}

def chunk_documents(state: IngestionState) -> IngestionState:
    print("--- Entering Node: chunk_documents ---")
    documents = state['doc_chunks']
    if not documents:
        return {"doc_chunks": [], "num_chunks": 0}
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    doc_chunks = text_splitter.split_documents(documents)
    return {"doc_chunks": doc_chunks, "num_chunks": len(doc_chunks)}

def embed_and_store(state: IngestionState) -> IngestionState:
    print("--- Entering Node: embed_and_store ---")
    doc_chunks = state['doc_chunks']
    if not doc_chunks:
        return state
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    chroma_client = get_chroma_client()
    Chroma.from_documents(documents=doc_chunks, embedding=embedding_model, client=chroma_client, collection_name="knowledge_base")
    print(f"--- Successfully embedded and stored {len(doc_chunks)} chunks in ChromaDB. ---")
    return state

# --- Graph Definition (Ingestion) ---
workflow = StateGraph(IngestionState)
workflow.add_node("download_and_load", download_and_load)
workflow.add_node("chunk_documents", chunk_documents)
workflow.add_node("embed_and_store", embed_and_store)
workflow.set_entry_point("download_and_load")
workflow.add_edge("download_and_load", "chunk_documents")
workflow.add_edge("chunk_documents", "embed_and_store")
workflow.add_edge("embed_and_store", END)
ingestion_graph = workflow.compile()


# ==============================================================================
# === ASYNC RAG GRAPH ==========================================================
# ==============================================================================

# --- Q&A State Definition ---
class QAState(TypedDict):
    question: str
    context: str
    answer: str
    citations: List[str]

# --- ASYNC Q&A Node Definitions ---
async def retrieve_documents(state: QAState) -> QAState:
    print("--- Entering ASYNC Node: retrieve_documents ---")
    question = state['question']
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    chroma_client = get_chroma_client()
    vectorstore = Chroma(client=chroma_client, collection_name="knowledge_base", embedding_function=embedding_model)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    retrieved_docs = await retriever.ainvoke(question)
    context = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
    citations = list(set([doc.metadata.get('source', 'Unknown') for doc in retrieved_docs]))
    return {"context": context, "citations": citations}

async def generate_answer(state: QAState) -> QAState:
    print("--- Entering ASYNC Node: generate_answer ---")
    question = state['question']
    context = state['context']
    prompt_template = "Answer the user's question based ONLY on the context provided:\n\nCONTEXT:\n{context}\n\nQUESTION:\n{question}"
    prompt = ChatPromptTemplate.from_template(prompt_template)
    
    # vvv THIS IS THE ONLY CHANGE IN THIS ENTIRE FILE vvv
    # Using the more stable "gemini-1.0-pro" model
    llm = ChatGoogleGenerativeAI(model="gemini-1.0-pro", temperature=0, convert_system_message_to_human=True)
    # ^^^ END OF CHANGE ^^^

    rag_chain = {"context": RunnablePassthrough(), "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
    answer = await rag_chain.ainvoke({"context": context, "question": question})
    return {"answer": answer}

# --- Q&A Graph Definition ---
qa_workflow = StateGraph(QAState)
qa_workflow.add_node("retrieve_documents", retrieve_documents)
qa_workflow.add_node("generate_answer", generate_answer)
qa_workflow.set_entry_point("retrieve_documents")
qa_workflow.add_edge("retrieve_documents", "generate_answer")
qa_workflow.add_edge("generate_answer", END)
qa_graph = qa_workflow.compile()