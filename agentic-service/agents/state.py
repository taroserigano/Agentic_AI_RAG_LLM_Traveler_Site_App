"""
State schema for LangGraph planner workflow.
Tracks data passed between agent nodes.
"""
from typing import TypedDict, Dict, Any, List, Optional


class PlannerState(TypedDict):
    """Shared state across all agent nodes."""
    
    # Request context
    run_id: str
    city: str
    country: str
    days: int
    budget: Optional[float]
    preferences: Dict[str, Any]
    user_id: Optional[str]
    
    # Agent outputs
    research_results: Dict[str, Any]
    logistics_plan: Dict[str, Any]
    compliance_checks: Dict[str, Any]
    experience_content: Dict[str, Any]
    
    # Final outputs
    final_tour: Dict[str, Any]
    citations: List[str]
    cost: Dict[str, Any]
    status: str
    errors: List[str]
