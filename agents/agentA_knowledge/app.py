# agents/agent_a/app.py

from fastapi import FastAPI
from pydantic import BaseModel

# --- Pydantic Models ---
# These models define the expected structure of your API requests and responses.
# FastAPI uses them to validate incoming data automatically.

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
    citations: list
    confidence: float


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
    automatically return a 422 error, which is what you were seeing.
    """
    # For now, this is a placeholder. Later, you will implement your
    # knowledge retrieval logic here using request.userId and request.text.
    
    print(f"Received question from userId: {request.userId}") # Good for debugging!

    # Return a sample response that matches the 'AskResponse' model.
    return AskResponse(
        answer="This is a placeholder answer from Agent A.",
        citations=["doc1.pdf"],
        confidence=0.95
    )