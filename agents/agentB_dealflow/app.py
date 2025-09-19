# agents/agent_b/app.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import datetime

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
    
class NextStepRequest(BaseModel):
    text: str

class NextStepResponse(BaseModel):
    title: str
    start_iso: str
    end_iso: str
    
# NEW: Models for the status update endpoint
class StatusClassifyRequest(BaseModel):
    """Defines the input for a status update."""
    label: str # "Won", "Lost", or "On hold"
    reasonText: Optional[str] = None # The user's explanation is optional

class StatusClassifyResponse(BaseModel):
    """Defines the output for a classified status."""
    label: str
    reasonCategory: str
    reasonSummary: str


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

@app.post("/agentB/nextstep-parse", response_model=NextStepResponse)
def nextstep_parse_endpoint(request: NextStepRequest):
    print(f"Received scheduling text: {request.text}")
    now = datetime.datetime.now(datetime.timezone.utc)
    start_time = now + datetime.timedelta(days=1)
    end_time = start_time + datetime.timedelta(hours=1)
    return NextStepResponse(
        title=f"Follow-up call based on: '{request.text}'",
        start_iso=start_time.isoformat(),
        end_iso=end_time.isoformat()
    )

# NEW: Endpoint for classifying a status update
@app.post("/agentB/status-classify", response_model=StatusClassifyResponse)
def status_classify_endpoint(request: StatusClassifyRequest):
    """Classifies a deal status update."""
    print(f"Received status update: {request.label} | Reason: {request.reasonText}")
    
    # In a real agent, an LLM would categorize the reason.
    # For now, we return a placeholder.
    category = "Budget"
    if "timeline" in (request.reasonText or ""):
        category = "Timeline"
        
    return StatusClassifyResponse(
        label=request.label,
        reasonCategory=category,
        reasonSummary=f"Placeholder summary for: {request.reasonText}"
    )