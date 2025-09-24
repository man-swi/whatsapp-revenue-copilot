from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from graph import ingestiongraph, IngestionState, qagraph, QAState

app = FastAPI(
    title="Agent A Knowledge Agent",
    description="Manages knowledge base ingestion and QA.",
    version="1.0.0"
)

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

@app.get("/")
async def read_root():
    return {"message": "Agent A is running."}

@app.post("/agentA/ask", response_model=AskResponse)
async def askendpoint(request: AskRequest):
    print("--- Received question for /agentA/ask ---")
    print("Question:", request.text)
    try:
        initialstate = {"question": request.text}
        # Use asynchronous invocation
        finalstate = await qagraph.ainvoke(initialstate, recursion_limit=10)
        print("--- QA Graph execution finished ---")
        answer = finalstate.get("answer", "I could not find an answer in the documents.")
        citations = finalstate.get("citations", [])
        return AskResponse(
            answer=answer,
            citations=citations,
            confidence=0.9  # Placeholder
        )
    except Exception as e:
        print("An error occurred in askendpoint:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agentA/ingest", response_model=IngestResponse)
async def ingestendpoint(request: IngestRequest):
    print("--- Received request for /agentA/ingest ---")
    try:
        initialstate = {"driveFileId": request.driveFileId}
        finalstate = await ingestiongraph.ainvoke(initialstate, recursion_limit=10)
        print("--- Ingestion Graph execution finished ---")
        return IngestResponse(
            chunks=finalstate.get("numchunks", 0),
            status=f"SUCCESS Processing complete for file {request.driveFileId}"
        )
    except Exception as e:
        print("An error occurred in ingestendpoint:", e)
        raise HTTPException(status_code=500, detail=str(e))
