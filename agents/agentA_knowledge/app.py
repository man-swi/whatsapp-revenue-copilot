from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
# Import the graph we just created
from graph import ingestion_graph, AgentState

# --- Pydantic Models ---
class AskRequest(BaseModel):
    """
    Defines the structure of the incoming request body for the /ask endpoint.
    It MUST have a 'userId' and a 'text' field.
    """
    userId: str
    text: str

class AskResponse(BaseModel):
    """
    Defines the structure of the outgoing response body from the /ask endpoint.
    """
    answer: str
    citations: List[str]
    confidence: float

class IngestRequest(BaseModel):
    driveFileId: str

class IngestResponse(BaseModel):
    chunks: int
    status: str

# --- FastAPI Application ---
app = FastAPI(
    title="Agent A: Knowledge Agent",
    description="Manages knowledge base ingestion and Q&A.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    """A simple endpoint to check if the agent is running."""
    return {"message": "Agent A is running."}

@app.post("/agentA/ask", response_model=AskResponse)
def ask_endpoint(request: AskRequest):
    """
    This is the main Q&A endpoint.
    It expects a JSON body matching the 'AskRequest' model.
    If the body is missing or the fields don't match, FastAPI will
    automatically return a 422 error.
    """
    print(f"Received question from userId: {request.userId}") # Good for debugging!

    # Return a sample response that matches the 'AskResponse' model.
    return AskResponse(
        answer="This is a placeholder answer from Agent A.",
        citations=["doc1.pdf"],
        confidence=0.95
    )

@app.post("/agentA/ingest", response_model=IngestResponse)
def ingest_endpoint(request: IngestRequest):
    """Receives a file ID from n8n and triggers the ingestion graph."""
    try:
        print(f"--- Received request for /agentA/ingest ---")
        
        # Create the initial state for our graph
        initial_state = AgentState(driveFileId=request.driveFileId)
        
        # Invoke the graph with the initial state
        final_state = ingestion_graph.invoke(initial_state)
        
        print(f"--- Graph execution finished ---")
        
        # Return a response based on the final state of the graph
        return IngestResponse(
            chunks=final_state.num_chunks,
            status=f"SUCCESS: Processing complete for file {request.driveFileId}"
        )

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))