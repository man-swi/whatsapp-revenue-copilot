from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableLambda

# --- State ---
# This defines the "memory" or state of our agent as it runs.
class AgentState(BaseModel):
    driveFileId: str = Field(..., description="The ID of the file in Google Drive to process.")
    num_chunks: int = Field(0, description="The number of chunks the document was split into.")

# --- Nodes ---
# Each function is a "node" in our graph that performs a specific action.

def process_document(state: AgentState) -> AgentState:
    """
    Placeholder node to simulate document processing.
    In the future, this node will contain all the logic for chunking and embedding.
    """
    print(f"--- Entering Node: process_document ---")
    print(f"Simulating processing for file: {state.driveFileId}")
    
    # Simulate the outcome
    num_chunks_processed = 150 # Placeholder
    
    print(f"Document was split into {num_chunks_processed} chunks.")
    
    # Update the state with the result
    state.num_chunks = num_chunks_processed
    return state

# --- Graph Definition ---
# This is where we would normally use LangGraph's StateGraph to connect the nodes.
# For now, we will create a simple chain to call our one node.

# This creates a simple "graph" that just calls our one processing function.
ingestion_graph = RunnableLambda(process_document)