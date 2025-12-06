"""
FastAPI Lambda version - simplified for travel planning only.
Vault and database features removed to avoid binary dependencies.
"""
import logging
import sys
import typing
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

from config_lambda import settings

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Python 3.12 compatibility
if sys.version_info >= (3, 12):
    _native_forward_eval = typing.ForwardRef._evaluate
    def _patched_forward_evaluate(self, globalns, localns, type_params=None, *, recursive_guard=None):
        guard = recursive_guard if recursive_guard is not None else set()
        return _native_forward_eval(self, globalns, localns, type_params, recursive_guard=guard)
    typing.ForwardRef._evaluate = _patched_forward_evaluate

# Import SimplePlanner
try:
    from agents.simple_planner_lambda import SimplePlanner as AgenticPlanner
    planner_initialization_error = None
except Exception as planner_error:
    logger.error(f"Planner import failed: {planner_error}", exc_info=True)
    AgenticPlanner = None
    planner_initialization_error = planner_error

app = FastAPI(
    title="Agentic Travel Planner - Lambda",
    description="Serverless travel itinerary generation",
    version="0.2.0"
)

# Validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error for {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lambda needs broader CORS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize planner
if AgenticPlanner is not None:
    try:
        planner = AgenticPlanner()
    except Exception as planner_error:
        logger.error("Planner initialization failed", exc_info=True)
        planner = None
        planner_initialization_error = planner_error
else:
    planner = None


class PlanRequest(BaseModel):
    """Request schema for itinerary planning."""
    city: str
    country: str
    days: int = 3
    budget: Optional[float] = None
    preferences: Optional[Any] = None
    user_id: Optional[str] = None


class PlanResponse(BaseModel):
    """Response schema with generated itinerary."""
    run_id: str
    tour: Dict[str, Any]
    cost: Dict[str, Any]
    citations: list[str]
    status: str


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "agentic-travel-planner-lambda",
        "status": "running",
        "version": "0.2.0"
    }


@app.post("/api/agentic/plan", response_model=PlanResponse)
async def create_plan(request: PlanRequest):
    """
    Generate multi-day itinerary using AI.
    """
    if planner is None:
        detail = "Planner unavailable"
        if planner_initialization_error:
            detail += f": {planner_initialization_error}"
        raise HTTPException(status_code=503, detail=detail)

    try:
        logger.info(f"Planning: {request.city}, {request.country} ({request.days} days)")
        
        prefs = request.preferences or {}
        if isinstance(prefs, list):
            prefs = {"tags": prefs}

        result = await planner.generate_itinerary(
            city=request.city,
            country=request.country,
            days=request.days,
            budget=request.budget,
            preferences=prefs,
            user_id=request.user_id
        )
        
        return PlanResponse(**result)
    
    except Exception as e:
        logger.error(f"Planning failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Planning error: {str(e)}")


@app.get("/api/agentic/status/{run_id}")
async def get_status(run_id: str):
    """Check status of a planning run."""
    return {"run_id": run_id, "status": "completed"}
