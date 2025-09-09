# agents/agentA_knowledge/app.py
from fastapi import FastAPI

app = FastAPI(
    title="Agent A: Knowledge Agent",
    description="Manages knowledge base ingestion and Q&A.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Agent A is running."}