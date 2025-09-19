# agents/agent_b/app.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

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

# NEW: Models for the proposal endpoint
class ProposalRequest(BaseModel):
    """Defines the input for a proposal request."""
    lead_company: str

class ProposalResponse(BaseModel):
    """Defines the output for a generated proposal."""
    title: str
    summary: str
    bullet_points: List[str]


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

# NEW: Endpoint for generating proposal copy
@app.post("/agentB/proposal-copy", response_model=ProposalResponse)
def proposal_copy_endpoint(request: ProposalRequest):
    """Generates placeholder proposal text for a given company."""
    print(f"Received proposal request for company: {request.lead_company}")
    return ProposalResponse(
        title=f"Proposal for {request.lead_company}",
        summary=f"This document outlines a proof of concept for {request.lead_company} to demonstrate value.",
        bullet_points=[
            "Initial consultation and goal alignment.",
            "Implementation of core features.",
            "Review session and next steps."
        ]
    )