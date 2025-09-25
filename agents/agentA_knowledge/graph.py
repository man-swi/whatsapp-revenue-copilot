# agents/agentA_knowledge/graph.py

from langgraph.graph import StateGraph, END
from typing import TypedDict, List
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
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

# --- State Definition (Ingestion) ---
class IngestionState(TypedDict):
    driveFileId: str
    doc_chunks: List
    num_chunks: int

# --- Node Definitions (Ingestion) ---
# ... [The ingestion nodes are synchronous and correct, so they remain unchanged] ...
def download_and_load(state: IngestionState) -> IngestionState:
    print("--- Entering Node: download_and_load ---")
    file_id = state['driveFileId']
    documents = []
    file_buffer = download_file_from_drive(file_id)
    if file_buffer is None:
        print("Failed to download file.")
        return {"doc_chunks": [], "num_chunks": 0}
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_buffer.getvalue())
            temp_file_path = temp_file.name
        print(f"File temporarily saved to: {temp_file_path}")
        if file_buffer.mimeType == 'application/pdf':
            loader = PyPDFLoader(temp_file_path)
            documents = loader.load()
            print(f"Successfully loaded {len(documents)} pages from PDF.")
        else:
            print(f"Unsupported file type: {file_buffer.mimeType}")
            documents = []
    finally:
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"Cleaned up temporary file: {temp_file_path}")
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
    print(f"Split document into {len(doc_chunks)} chunks.")
    return {"doc_chunks": doc_chunks, "num_chunks": len(doc_chunks)}

def embed_and_store(state: IngestionState) -> IngestionState:
    print("--- Entering Node: embed_and_store ---")
    doc_chunks = state['doc_chunks']
    if not doc_chunks:
        return state
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    chroma_client = get_chroma_client()
    Chroma.from_documents(
        documents=doc_chunks,
        embedding=embedding_model,
        client=chroma_client,
        collection_name="knowledge_base"
    )
    print(f"--- Successfully embedded and stored {len(doc_chunks)} chunks in ChromaDB. ---")
    return state

# --- Graph Definition (Ingestion) ---
ingestion_workflow = StateGraph(IngestionState)
ingestion_workflow.add_node("download_and_load", download_and_load)
ingestion_workflow.add_node("chunk_documents", chunk_documents)
ingestion_workflow.add_node("embed_and_store", embed_and_store)
ingestion_workflow.set_entry_point("download_and_load")
ingestion_workflow.add_edge("download_and_load", "chunk_documents")
ingestion_workflow.add_edge("chunk_documents", "embed_and_store")
ingestion_workflow.add_edge("embed_and_store", END)
ingestion_graph = ingestion_workflow.compile()


# ==============================================================================
# === Q&A GRAPH (RAG) - NOW FULLY SYNCHRONOUS =================================
# ==============================================================================

class QAState(TypedDict):
    question: str
    context: str
    answer: str
    citations: List[str]

def retrieve_documents(state: QAState) -> QAState:
    print("--- Entering Node: retrieve_documents ---")
    question = state['question']
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    chroma_client = get_chroma_client()
    vectorstore = Chroma(
        client=chroma_client,
        collection_name="knowledge_base",
        embedding_function=embedding_model,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    retrieved_docs = retriever.invoke(question) # Using synchronous invoke
    context = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
    citations = list(set([doc.metadata.get('source', 'Unknown') for doc in retrieved_docs]))
    print(f"Retrieved {len(retrieved_docs)} documents for question.")
    return {"context": context, "citations": citations}

def generate_answer(state: QAState) -> QAState:
    print("--- Entering Node: generate_answer ---")
    question = state['question']
    context = state['context']
    if not context:
        return {"answer": "I could not find any relevant information in the documents to answer your question."}
    prompt_template = "Answer the user's question based ONLY on the context provided.\n\nCONTEXT:\n{context}\n\nQUESTION:\n{question}\n\nANSWER:"
    prompt = ChatPromptTemplate.from_template(prompt_template)
    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
    rag_chain = prompt | llm | StrOutputParser()
    answer = rag_chain.invoke({"context": context, "question": question}) # Using synchronous invoke
    return {"answer": answer}

# --- Q&A Graph Definition ---
qa_workflow = StateGraph(QAState)
qa_workflow.add_node("retrieve_documents", retrieve_documents)
qa_workflow.add_node("generate_answer", generate_answer)
qa_workflow.set_entry_point("retrieve_documents")
qa_workflow.add_edge("retrieve_documents", "generate_answer")
qa_workflow.add_edge("generate_answer", END)
qa_graph = qa_workflow.compile()