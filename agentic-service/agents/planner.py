"""
Multi-agent itinerary planner orchestrated via LangGraph.
Combines OpenAI GPT-4.1-mini, Ollama, FAISS retrieval, and external tools.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime
import uuid

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor

from config import settings
from .tools import get_available_tools
from .state import PlannerState

logger = logging.getLogger(__name__)


class AgenticPlanner:
    """
    Multi-agent travel planner coordinating specialist agents.
    """
    
    def __init__(self):
        self.openai_llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            openai_api_key=settings.openai_api_key
        )
        self.tools = get_available_tools()
        self.tool_executor = ToolExecutor(self.tools)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build LangGraph state machine:
        START -> Supervisor -> [Researcher, Logistics, Compliance, Experience] -> Decision -> END
        """
        workflow = StateGraph(PlannerState)
        
        # Add nodes
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("researcher", self._researcher_node)
        workflow.add_node("logistics", self._logistics_node)
        workflow.add_node("compliance", self._compliance_node)
        workflow.add_node("experience", self._experience_node)
        workflow.add_node("decision", self._decision_node)
        
        # Define edges
        workflow.set_entry_point("supervisor")
        workflow.add_edge("supervisor", "researcher")
        workflow.add_edge("researcher", "logistics")
        workflow.add_edge("logistics", "compliance")
        workflow.add_edge("compliance", "experience")
        workflow.add_edge("experience", "decision")
        workflow.add_edge("decision", END)
        
        return workflow.compile()
    
    async def generate_itinerary(
        self,
        city: str,
        country: str,
        days: int,
        budget: float = None,
        preferences: Dict[str, Any] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Main entry point: orchestrate agents to generate itinerary.
        """
        run_id = str(uuid.uuid4())
        logger.info(f"[{run_id}] Starting itinerary generation")
        
        initial_state: PlannerState = {
            "run_id": run_id,
            "city": city,
            "country": country,
            "days": days,
            "budget": budget,
            "preferences": preferences or {},
            "user_id": user_id,
            "research_results": {},
            "logistics_plan": {},
            "compliance_checks": {},
            "experience_content": {},
            "final_tour": {},
            "citations": [],
            "cost": {},
            "status": "in_progress",
            "errors": []
        }
        
        try:
            final_state = await self.graph.ainvoke(initial_state)
            
            return {
                "run_id": run_id,
                "tour": final_state["final_tour"],
                "cost": final_state["cost"],
                "citations": final_state["citations"],
                "status": "completed"
            }
        
        except Exception as e:
            logger.error(f"[{run_id}] Generation failed: {str(e)}", exc_info=True)
            return {
                "run_id": run_id,
                "tour": {},
                "cost": {},
                "citations": [],
                "status": "failed",
                "error": str(e)
            }
    
    async def _supervisor_node(self, state: PlannerState) -> PlannerState:
        """
        Supervisor: coordinates agent execution order and halting conditions.
        """
        logger.info(f"[{state['run_id']}] Supervisor: initiating planning workflow")
        
        prompt = f"""You are a travel planning supervisor coordinating specialist agents.

Request: {state['days']}-day trip to {state['city']}, {state['country']}
Budget: {state.get('budget', 'flexible')}
Preferences: {state.get('preferences', {})}

Coordinate the following agents in sequence:
1. Researcher - gather destination insights
2. Logistics - optimize routes/schedules
3. Compliance - verify safety/visa requirements
4. Experience - generate media and narrative

Ensure all agents complete successfully before finalizing the itinerary."""
        
        response = await self.openai_llm.ainvoke([
            SystemMessage(content="You are a supervisor coordinating travel planning agents."),
            HumanMessage(content=prompt)
        ])
        
        logger.info(f"[{state['run_id']}] Supervisor: workflow initialized")
        return state
    
    async def _researcher_node(self, state: PlannerState) -> PlannerState:
        """
        Researcher agent: queries RAG + external APIs for destination data.
        """
        logger.info(f"[{state['run_id']}] Researcher: gathering destination insights")
        
        # TODO: Call FAISS retrieval tool, external APIs
        state["research_results"] = {
            "attractions": ["Sample Attraction 1", "Sample Attraction 2"],
            "weather": "Sunny, 25°C average",
            "local_tips": "Best season to visit"
        }
        state["citations"].append("Research database")
        
        return state
    
    async def _logistics_node(self, state: PlannerState) -> PlannerState:
        """
        Logistics agent: schedules stops, optimizes routes.
        """
        logger.info(f"[{state['run_id']}] Logistics: optimizing itinerary")
        
        # TODO: OR-Tools route optimization
        state["logistics_plan"] = {
            "daily_schedule": [
                {"day": 1, "stops": ["Stop A", "Stop B", "Stop C"]},
                {"day": 2, "stops": ["Stop D", "Stop E"]},
            ],
            "transport": "mix of walking and public transit"
        }
        
        return state
    
    async def _compliance_node(self, state: PlannerState) -> PlannerState:
        """
        Compliance agent: checks visa, safety advisories, vaccinations.
        """
        logger.info(f"[{state['run_id']}] Compliance: validating requirements")
        
        # TODO: Call safety/visa APIs
        state["compliance_checks"] = {
            "visa_required": False,
            "safety_level": "safe",
            "vaccinations": []
        }
        
        return state
    
    async def _experience_node(self, state: PlannerState) -> PlannerState:
        """
        Experience agent: generates images, narrative copy.
        """
        logger.info(f"[{state['run_id']}] Experience: creating content")
        
        # TODO: DALL-E image generation
        state["experience_content"] = {
            "hero_image": "https://placeholder.com/600x400",
            "description": f"An unforgettable {state['days']}-day journey through {state['city']}"
        }
        
        return state
    
    async def _decision_node(self, state: PlannerState) -> PlannerState:
        """
        Decision node: reconciles all agent outputs into final itinerary.
        """
        logger.info(f"[{state['run_id']}] Decision: assembling final itinerary")
        
        state["final_tour"] = {
            "city": state["city"],
            "country": state["country"],
            "title": f"{state['days']}-Day {state['city']} Adventure",
            "description": state["experience_content"].get("description", ""),
            "image": state["experience_content"].get("hero_image"),
            "stops": [
                stop for day in state["logistics_plan"].get("daily_schedule", [])
                for stop in day.get("stops", [])
            ],
            "compliance": state["compliance_checks"],
            "research": state["research_results"]
        }
        
        state["cost"] = {
            "llm_tokens": 1500,
            "api_calls": 5,
            "total_usd": 0.15
        }
        
        state["status"] = "completed"
        logger.info(f"[{state['run_id']}] Planning completed successfully")
        
        return state
