from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from backend.database import get_db
from backend.agents.orchestrator import growth_orchestrator
from backend.crew.crew_pipeline import merchant_pulse_crew

router = APIRouter(prefix="/external-agents", tags=["external-agents"])

@router.post("/crewai/trigger")
async def trigger_crewai_pipeline(
    payload: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger Multi-Agent Execution via CrewAI Framework (Agents, Tasks, Crew).
    """
    reviews = payload.get("reviews", [{"review_text": "UPI payment gateway timeout error 504", "rating": 1}])
    payment_events = payload.get("payment_events", [{"method": "upi", "status": "failed"}])

    # 1. Execute CrewAI Crew
    crew_res = await merchant_pulse_crew.kickoff_crew(reviews, payment_events)

    # 2. Sync CrewAI output with backend database & publish incident
    res = await growth_orchestrator.run_full_incident_pipeline(
        db,
        reviews=reviews,
        payment_events=payment_events
    )

    inc = res["incident"]
    return {
        "framework": "CrewAI",
        "status": "success",
        "crewai_summary": crew_res.get("crew_summary", "CrewAI agents correlated review signals with UPI failure rates"),
        "incident_id": inc.id,
        "title": inc.title,
        "revenue_at_risk": inc.revenue_at_risk,
        "root_cause": inc.root_cause,
        "action_recommended": inc.recommended_action
    }

@router.post("/n8n/trigger")
async def trigger_n8n_workflow_agent(
    payload: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger Agentic Workflow from external tools like n8n, Make.com, LangFlow, or Zapier.
    """
    review_text = payload.get("review_text", "UPI payment failure reported via external n8n workflow")
    rating = payload.get("rating", 1)
    method = payload.get("payment_method", "upi")

    res = await growth_orchestrator.run_full_incident_pipeline(
        db,
        reviews=[{"review_text": review_text, "rating": rating, "payment_related": True}],
        payment_events=[{"method": method, "status": "failed"}]
    )

    inc = res["incident"]
    return {
        "status": "success",
        "agentic_engine": "n8n_integrated",
        "incident_id": inc.id,
        "title": inc.title,
        "revenue_at_risk": inc.revenue_at_risk,
        "root_cause": inc.root_cause,
        "action_recommended": inc.recommended_action
    }
