from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
# Import the graph and the NEW state object we created
from graph import ingestion_graph, IngestionState # CHANGED THIS LINE

# --- Pydantic Models ---
class AskRequest(BaseModel):
    userId: str
    text: str

class AskResponse(BaseModel):
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
    return {"message": "Agent A is running."}

@app.post("/agentA/ask", response_model=AskResponse)
def ask_endpoint(request: AskRequest):
    print(f"Received question from userId: {request.userId}")
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
        
        # Create the initial state for our graph, using the NEW state name
        initial_state = {"driveFileId": request.driveFileId} # CHANGED THIS LINE
        
        # Invoke the graph with the initial state
        # The config is necessary for streaming logs in LangSmith, good practice
        final_state = ingestion_graph.invoke(initial_state, {"recursion_limit": 10})
        
        print(f"--- Graph execution finished ---")
        
        # Return a response based on the final state of the graph
        return IngestResponse(
            chunks=final_state.get('num_chunks', 0), # CHANGED THIS LINE to safely get the value
            status=f"SUCCESS: Processing complete for file {request.driveFileId}"
        )

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))