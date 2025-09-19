# agents/agent_b/app.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import datetime # We need this for the new endpoint

# --- Pydantic Models ---

class NewLeadRequest(BaseModel):
    raw: str

class NewLeadResponse(BaseModel):
    name: str
    company: str
    intent: str
    budget: int

class ProposalRequest(BaseModel):
    lead_company: str

class ProposalResponse(BaseModel):
    title: str
    summary: str
    bullet_points: List[str]
    
# NEW: Models for the scheduling endpoint
class NextStepRequest(BaseModel):
    """Defines the input for a scheduling request."""
    text: str

class NextStepResponse(BaseModel):
    """Defines the output for a parsed time."""
    title: str
    start_iso: str
    end_iso: str


# --- FastAPI Application ---
app = FastAPI(
    title="Agent B: Dealflow Agent",
    description="Manages lead capture, proposals, and deal status.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Agent B is running."}


@app.post("/agentB/newlead", response_model=NewLeadResponse)
def newlead_endpoint(request: NewLeadRequest):
    print(f"Received raw lead text: {request.raw}")
    return NewLeadResponse(
        name="John Doe",
        company="Acme Corp",
        intent="Proof of Concept",
        budget=10000
    )

@app.post("/agentB/proposal-copy", response_model=ProposalResponse)
def proposal_copy_endpoint(request: ProposalRequest):
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

# NEW: Endpoint for parsing scheduling text
@app.post("/agentB/nextstep-parse", response_model=NextStepResponse)
def nextstep_parse_endpoint(request: NextStepRequest):
    """Parses scheduling text and returns placeholder ISO times."""
    print(f"Received scheduling text: {request.text}")
    
    # In a real agent, you would use an LLM to parse the text.
    # For now, we'll return a fixed time.
    now = datetime.datetime.now(datetime.timezone.utc)
    start_time = now + datetime.timedelta(days=1)
    end_time = start_time + datetime.timedelta(hours=1)
    
    return NextStepResponse(
        title=f"Follow-up call based on: '{request.text}'",
        start_iso=start_time.isoformat(),
        end_iso=end_time.isoformat()
    )