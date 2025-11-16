"""
FastAPI entrypoint for agentic travel planner service.
Exposes endpoints for multi-agent itinerary generation.
"""
import logging
import sys
import typing
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from config import settings
if sys.version_info >= (3, 12):
    _native_forward_eval = typing.ForwardRef._evaluate


    def _patched_forward_evaluate(self, globalns, localns, type_params=None, *, recursive_guard=None):
        guard = recursive_guard if recursive_guard is not None else set()
        return _native_forward_eval(self, globalns, localns, type_params, recursive_guard=guard)


    typing.ForwardRef._evaluate = _patched_forward_evaluate

from services.vault import VaultIngestionService

try:
    from agents.planner import AgenticPlanner
except Exception as planner_import_error:  # noqa: BLE001
    AgenticPlanner = None  # type: ignore[assignment]
    planner_initialization_error: Optional[Exception] = planner_import_error
else:
    planner_initialization_error: Optional[Exception] = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agentic Travel Planner",
    description="Multi-agent LangGraph service for itinerary generation",
    version="0.1.0"
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize planner lazily so ingestion routes still work if LangChain stack is misconfigured.
if AgenticPlanner is not None:
    try:
        planner = AgenticPlanner()
    except Exception as planner_error:  # noqa: BLE001
        logger.error("Planner initialization failed", exc_info=True)
        planner = None
        planner_initialization_error = planner_error
else:
    planner = None

vault_service = VaultIngestionService()


class PlanRequest(BaseModel):
    """Request schema for itinerary planning."""
    city: str
    country: str
    days: int = 3
    budget: Optional[float] = None
    preferences: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None


class PlanResponse(BaseModel):
    """Response schema with generated itinerary."""
    run_id: str
    tour: Dict[str, Any]
    cost: Dict[str, Any]
    citations: list[str]
    status: str


class VaultUploadResponse(BaseModel):
    """Response payload for knowledge vault ingestions."""
    documentId: str
    chunkCount: int
    tokenEstimate: int
    message: str


class VaultQueryRequest(BaseModel):
    """Request schema for querying knowledge vault."""
    query: str
    user_id: str
    top_k: int = 3


class VaultQueryResponse(BaseModel):
    """Response schema for vault query with RAG answer."""
    answer: str
    chunks: list[Dict[str, Any]]
    citations: list[Dict[str, str]]
    tokens_used: Optional[int] = None


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "agentic-travel-planner",
        "status": "running",
        "version": "0.1.0"
    }


@app.post("/api/agentic/plan", response_model=PlanResponse)
async def create_plan(request: PlanRequest):
    """
    Generate multi-day itinerary using agent orchestration.
    
    Workflow:
    1. Supervisor spawns specialist agents
    2. Researcher queries RAG + external APIs
    3. Logistics optimizes route/schedule
    4. Compliance checks safety/visas
    5. Experience generates media/copy
    6. Decision node reconciles, persists to DB
    """
    if planner is None:
        detail = "Planner stack is unavailable. Check server logs for LangChain initialization errors."
        if planner_initialization_error:
            detail += f" Reason: {planner_initialization_error}"
        raise HTTPException(status_code=503, detail=detail)

    try:
        logger.info(f"Planning request: {request.city}, {request.country} ({request.days} days)")
        
        result = await planner.generate_itinerary(
            city=request.city,
            country=request.country,
            days=request.days,
            budget=request.budget,
            preferences=request.preferences or {},
            user_id=request.user_id
        )
        
        return PlanResponse(**result)
    
    except Exception as e:
        logger.error(f"Planning failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Planning error: {str(e)}")


@app.get("/api/agentic/status/{run_id}")
async def get_status(run_id: str):
    """Check status of a planning run."""
    # TODO: query agent run logs from DB
    return {"run_id": run_id, "status": "completed"}


@app.post("/api/v1/vault/upload", response_model=VaultUploadResponse)
async def ingest_vault_document(
    file: UploadFile = File(...),
    documentId: str = Form(...),
    userId: str = Form(...),
    title: str = Form(...),
    notes: Optional[str] = Form(None),
):
    """
    Accept a user-uploaded document, extract text, chunk, embed, and persist to FAISS.
    The Next.js app stores metadata in Postgres; this endpoint handles vector indexing.
    """
    try:
        result = vault_service.ingest_document(
            upload=file,
            document_id=documentId,
            user_id=userId,
            title=title,
            notes=notes,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.error("Vault ingestion failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Vault ingestion failed.") from exc


@app.post("/api/v1/vault/query", response_model=VaultQueryResponse)
async def query_vault_documents(request: VaultQueryRequest):
    """
    RAG query endpoint: retrieve relevant document chunks and generate answer.
    Filters results by user_id to ensure data isolation.
    """
    try:
        logger.info(f"Vault query from user {request.user_id}: {request.query}")
        
        result = vault_service.generate_answer(
            query=request.query,
            user_id=request.user_id,
            top_k=request.top_k,
        )
        
        return VaultQueryResponse(**result)
    
    except Exception as exc:  # noqa: BLE001
        logger.error("Vault query failed", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(exc)}") from exc


@app.post("/api/v1/vault/query-stream")
async def query_vault_documents_stream(request: VaultQueryRequest):
    """
    RAG query endpoint with streaming: retrieve chunks and stream OpenAI response.
    Returns Server-Sent Events for progressive token display.
    """
    try:
        logger.info(f"Vault streaming query from user {request.user_id}: {request.query}")
        
        return StreamingResponse(
            vault_service.generate_answer_stream(
                query=request.query,
                user_id=request.user_id,
                top_k=request.top_k,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    
    except Exception as exc:  # noqa: BLE001
        logger.error("Vault streaming query failed", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Streaming query failed: {str(exc)}") from exc


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
