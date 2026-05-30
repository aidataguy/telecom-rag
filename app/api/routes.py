from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.core.rag import rag_query, rag_streamer

app = FastAPI(title="TelecomOps RAG API", version="1.0")

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: list[dict]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    try:
        result = rag_query(req.query, req.top_k)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/stream")
async def query_stream(req: QueryRequest):
    """Stream response token by token."""
    async def token_generator():
        for token in rag_streamer(req.query, req.top_k):
            yield token

    return StreamingResponse(
        token_generator(),
        media_type="text/plain",
        headers={
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

