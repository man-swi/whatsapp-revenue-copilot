from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Agent B: Dealflow Agent",
    description="Manages lead capture, proposals, and deal status.",
    version="1.0.0"
)

class NewLeadRequest(BaseModel):
    raw: str

class NewLeadResponse(BaseModel):
    name: str
    company: str
    intent: str
    budget: int

@app.get("/")
def read_root():
    return {"message": "Agent B is running."}

@app.post("/agentB/newlead", response_model=NewLeadResponse)
def newlead_endpoint(request: NewLeadRequest):
    # TODO: implement your logic here
    return NewLeadResponse(name="John", company="Acme", intent="PoC", budget=10000)
