# agents/agentB_dealflow/app.py
from fastapi import FastAPI

app = FastAPI(
    title="Agent B: Dealflow Agent",
    description="Manages lead capture, proposals, and deal status.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Agent B is running."}

# We will add POST endpoints like /newlead, /proposal-copy later