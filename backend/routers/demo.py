import uuid
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select

from backend.database import get_db
from backend.models import Review, Incident, AgentEvent, Transaction, RecoveryAttempt
from backend.schemas import SimulateIncidentRequest, SetHealthRequest
from backend.providers.payment_provider import get_payment_provider
from backend.providers.review_provider import get_review_provider
from backend.agents.orchestrator import growth_orchestrator

router = APIRouter(prefix="/demo", tags=["demo"])

@router.post("/simulate-incident")
async def simulate_incident(req: SimulateIncidentRequest = SimulateIncidentRequest(), db: AsyncSession = Depends(get_db)):
    # 1. Update Payment Health to Degraded
    payment_provider = get_payment_provider()
    payment_provider.set_method_health("upi", "degraded", 0.82)
    
    # 2. Inject Play Store Reviews
    review_provider = get_review_provider(req.app_id)
    reviews_data = await review_provider.fetch_reviews(req.app_id, count=req.reviews_count or 25)
    
    inserted_reviews = []
    for r in reviews_data:
        rev_id = f"rev_{uuid.uuid4().hex[:8]}"
        review_obj = Review(
            id=rev_id,
            external_review_id=r.get("external_review_id", ""),
            customer_name=r.get("customer_name", "Anonymous"),
            rating=r.get("rating", 1),
            review_text=r.get("review_text", ""),
            app_version=r.get("app_version", "v3.4.2"),
            device=r.get("device", "Android"),
            sentiment=r.get("sentiment", "negative"),
            category=r.get("category", "payment_failure"),
            severity=r.get("severity", "high"),
            payment_related=r.get("payment_related", True),
            processed=True,
            ai_confidence=0.94
        )
        db.add(review_obj)
        inserted_reviews.append(r)
        
    await db.commit()

    # 3. Trigger Full Multi-Agent Pipeline via Orchestrator
    result = await growth_orchestrator.run_full_incident_pipeline(
        db, 
        reviews=inserted_reviews, 
        payment_events=[{"method": "upi", "status": "failed", "reason": "bank_timeout"}] * 42
    )

    return {
        "status": "success",
        "message": "Simulated UPI Payment Incident successfully triggered!",
        "incident_id": result["incident"].id,
        "revenue_at_risk": result["incident"].revenue_at_risk,
        "mttd": "2m 41s",
        "reviews_injected": len(inserted_reviews),
        "upi_health": "degraded (82% success rate)"
    }

@router.post("/set-health")
async def set_payment_health(req: SetHealthRequest):
    payment_provider = get_payment_provider()
    payment_provider.set_method_health(req.method, req.status, req.success_rate)
    return {"message": f"Updated {req.method} health to {req.status} ({req.success_rate * 100}%)"}

@router.post("/reset")
async def reset_demo(db: AsyncSession = Depends(get_db)):
    # Reset Payment Health
    payment_provider = get_payment_provider()
    payment_provider.set_method_health("upi", "healthy", 0.95)
    
    # Delete non-baseline incidents, events, reviews, and transactions
    await db.execute(delete(Incident))
    await db.execute(delete(AgentEvent))
    await db.execute(delete(RecoveryAttempt))
    await db.execute(delete(Review))
    await db.execute(delete(Transaction).where(Transaction.is_recovered == True))
    await db.commit()
    
    return {"message": "Demo state reset to baseline successfully."}
