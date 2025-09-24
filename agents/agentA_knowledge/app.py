# agents/agentA_knowledge/app.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
# Import ALL the graphs and state objects we created
from graph import ingestion_graph, IngestionState, qa_graph, QAState

# --- Pydantic Models ---
class AskRequest(BaseModel):
    userId: str
    text: str

class AskResponse(BaseModel):
    answer: str
    citations: List[str] = Field(default_factory=list)
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
    """Receives a question and uses the RAG graph to answer it."""
    try:
        print(f"--- Received question for /agentA/ask ---")
        print(f"Question: {request.text}")

        # Initial state for the QA graph
        initial_state = {"question": request.text}
        
        # Invoke the QA graph
        final_state = qa_graph.invoke(initial_state, {"recursion_limit": 10})

        print(f"--- Q&A Graph execution finished ---")
        
        answer = final_state.get('answer', "I could not find an answer in the documents.")
        citations = final_state.get('citations', [])

        return AskResponse(
            answer=answer,
            citations=citations,
            confidence=0.9 # Placeholder confidence for now
        )
    except Exception as e:
        print(f"An error occurred in ask_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agentA/ingest", response_model=IngestResponse)
def ingest_endpoint(request: IngestRequest):
    """Receives a file ID from n8n and triggers the ingestion graph."""
    try:
        print(f"--- Received request for /agentA/ingest ---")
        
        initial_state = {"driveFileId": request.driveFileId}
        
        final_state = ingestion_graph.invoke(initial_state, {"recursion_limit": 10})
        
        print(f"--- Ingestion Graph execution finished ---")
        
        return IngestResponse(
            chunks=final_state.get('num_chunks', 0),
            status=f"SUCCESS: Processing complete for file {request.driveFileId}"
        )

    except Exception as e:
        print(f"An error occurred in ingest_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))