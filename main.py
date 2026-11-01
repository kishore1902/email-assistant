from fastapi import FastAPI
from pydantic import BaseModel
import traceback
import agent
from indexer import col, sync_mailbox

app = FastAPI(title="Email Assistant")


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


@app.get("/status")
def status():
    return {"indexed_chunks": col.count()}


@app.post("/sync")
def sync(limit: int = 100):
    return {"new_emails_indexed": sync_mailbox(limit=limit)}


@app.post("/chat")
def chat(req: ChatRequest):
    try:
        return {"answer": agent.handle(req.message, req.history)}
    except Exception as ex:
        traceback.print_exc()
        return {"answer": f"⚠️ Something went wrong: {type(ex).__name__}: {ex}"}