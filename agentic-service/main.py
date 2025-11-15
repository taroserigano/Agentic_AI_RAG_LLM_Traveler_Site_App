"""
FastAPI entrypoint for agentic travel planner service.
Exposes endpoints for multi-agent itinerary generation.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from config import settings
from agents.planner import AgenticPlanner

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

# Initialize planner
planner = AgenticPlanner()


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
