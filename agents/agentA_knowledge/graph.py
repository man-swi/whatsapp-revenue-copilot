# agents/agentA_knowledge/graph.py

from langchain_core.pydantic_v1 import BaseModel, Field
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator
import tempfile # <--- ADDED
import os       # <--- ADDED

# Import our new tools
from tools import download_file_from_drive, get_chroma_client

# Import LangChain components for document processing
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# --- State Definition ---
# This is the memory of our graph.
class IngestionState(TypedDict):
    driveFileId: str
    doc_chunks: List # This will hold the document chunks after splitting
    num_chunks: int

# --- Node Definitions ---
# Each function is a "node" in our graph that performs a specific action.

# vvv THIS IS THE UPDATED FUNCTION vvv
def download_and_load(state: IngestionState) -> IngestionState:
    """
    Node 1: Downloads the file from Google Drive, saves it temporarily, and loads it.
    """
    print("--- Entering Node: download_and_load ---")
    file_id = state['driveFileId']
    documents = [] # Initialize documents list
    
    # Download the file using our tool
    file_buffer = download_file_from_drive(file_id)
    
    if file_buffer is None:
        print("Failed to download file.")
        return {"doc_chunks": [], "num_chunks": 0}

    # Use a temporary file to load the document from its path
    # This is necessary because PyPDFLoader expects a file path, not an in-memory object
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_buffer.getvalue())
            temp_file_path = temp_file.name
        
        print(f"File temporarily saved to: {temp_file_path}")

        # Check the MIME type to decide how to load the document
        if file_buffer.mimeType == 'application/pdf':
            # Use PyPDFLoader to load the PDF content from the temporary file path
            loader = PyPDFLoader(temp_file_path)
            documents = loader.load()
            print(f"Successfully loaded {len(documents)} pages from PDF.")
        else:
            print(f"Unsupported file type: {file_buffer.mimeType}")
            documents = []

    finally:
        # Clean up the temporary file
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"Cleaned up temporary file: {temp_file_path}")

    # Add source metadata to each document for later citation
    for doc in documents:
        doc.metadata["source"] = file_buffer.name
        
    return {"doc_chunks": documents}
# ^^^ END OF UPDATED FUNCTION ^^^


def chunk_documents(state: IngestionState) -> IngestionState:
    """
    Node 2: Splits the loaded documents into smaller chunks.
    """
    print("--- Entering Node: chunk_documents ---")
    documents = state['doc_chunks']
    
    if not documents:
        return {"doc_chunks": [], "num_chunks": 0}

    # Initialize a text splitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    # Split the documents into chunks
    doc_chunks = text_splitter.split_documents(documents)
    
    print(f"Split document into {len(doc_chunks)} chunks.")
    
    return {"doc_chunks": doc_chunks, "num_chunks": len(doc_chunks)}

def embed_and_store(state: IngestionState) -> IngestionState:
    """
    Node 3: Creates vector embeddings for the chunks and stores them in ChromaDB.
    """
    print("--- Entering Node: embed_and_store ---")
    doc_chunks = state['doc_chunks']
    
    if not doc_chunks:
        return state # Nothing to do

    # Initialize the embedding model. This will run locally inside the container.
    # "all-MiniLM-L6-v2" is a small, fast, and effective model.
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Initialize our ChromaDB client from tools.py
    chroma_client = get_chroma_client()
    
    # Create a Chroma vector store. This will add the new chunks to our persistent database.
    # We give it a collection name to keep things organized.
    vectorstore = Chroma.from_documents(
        documents=doc_chunks,
        embedding=embedding_model,
        client=chroma_client,
        collection_name="knowledge_base"
    )
    print(f"--- Successfully embedded and stored {len(doc_chunks)} chunks in ChromaDB. ---")
    
    return state

# --- Graph Definition ---
# This is where we wire the nodes together into a pipeline.

# 1. Initialize the StateGraph with our IngestionState memory structure.
workflow = StateGraph(IngestionState)

# 2. Add the nodes to the graph.
workflow.add_node("download_and_load", download_and_load)
workflow.add_node("chunk_documents", chunk_documents)
workflow.add_node("embed_and_store", embed_and_store)

# 3. Define the edges (the order of operations).
workflow.set_entry_point("download_and_load")
workflow.add_edge("download_and_load", "chunk_documents")
workflow.add_edge("chunk_documents", "embed_and_store")
workflow.add_edge("embed_and_store", END) # Mark the end of the graph

# 4. Compile the graph into a runnable object.
ingestion_graph = workflow.compile()