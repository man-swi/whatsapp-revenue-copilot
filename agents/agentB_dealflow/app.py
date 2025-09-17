# agents/agent_b/app.py

from fastapi import FastAPI
from pydantic import BaseModel

# --- Pydantic Models ---

class NewLeadRequest(BaseModel):
    """
    Defines the structure for an incoming new lead.
    For now, it just expects a raw text string.
    """
    raw: str

class NewLeadResponse(BaseModel):
    """
    Defines the structure of the data after the lead text has been processed.
    """
    name: str
    company: str
    intent: str
    budget: int


# --- FastAPI Application ---
app = FastAPI(
    title="Agent B: Dealflow Agent",
    description="Manages lead capture, proposals, and deal status.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    """A simple endpoint to check if the agent is running."""
    return {"message": "Agent B is running."}


@app.post("/agentB/newlead", response_model=NewLeadResponse)
def newlead_endpoint(request: NewLeadRequest):
    """
    This endpoint will process incoming text from a potential lead.
    """
    # TODO: Implement your lead processing logic here.
    # You will use an LLM or regex to extract details from 'request.raw'.
    
    print(f"Received raw lead text: {request.raw}") # Good for debugging!

    # Return a sample response for now.
    return NewLeadResponse(
        name="John Doe",
        company="Acme Corp",
        intent="Proof of Concept",
        budget=10000
    )