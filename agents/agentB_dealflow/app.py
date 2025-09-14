from pydantic import BaseModel

class NewLeadRequest(BaseModel):
    raw: str

class NewLeadResponse(BaseModel):
    name: str
    company: str
    intent: str
    budget: int
    # ... more fields as per contract

@app.post("/agentB/newlead", response_model=NewLeadResponse)
def newlead_endpoint(request: NewLeadRequest):
    # TODO: Parse and return lead struct
    return NewLeadResponse(name="John", company="Acme", intent="PoC", budget=10000)
