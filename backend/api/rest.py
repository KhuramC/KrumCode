import logging

from fastapi import APIRouter, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logger = logging.getLogger("api.routes")

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


@router.get("/api/health", status_code=status.HTTP_200_OK)
async def health():
    """Sanity check for the API."""
    return {"message": "RAG API is running."}


@router.post("/api/query", status_code=status.HTTP_200_OK)
async def query(request: Request, body: QueryRequest) -> StreamingResponse:
    """Queries the RAG engine and streams the response back."""
    query_engine = request.app.state.query_engine
    response = query_engine.query(body.question)

    def stream():
        for token in response.response_gen:
            yield token

    return StreamingResponse(stream(), media_type="text/plain")


# TODO: add endpoint for ingestion and end point for syncing