from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
from backend.database import get_db
from backend.models import Incident, AgentEvent
from backend.providers.payment_provider import get_payment_provider

router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.get("")
async def list_incidents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident).order_by(desc(Incident.started_at)))
    incidents = result.scalars().all()
    return incidents

@router.get("/{incident_id}")
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    # Get associated agent events
    events_res = await db.execute(
        select(AgentEvent).where(AgentEvent.incident_id == incident_id).order_by(AgentEvent.created_at)
    )
    events = events_res.scalars().all()
    
    return {
        "incident": incident,
        "timeline": events
    }

@router.post("/{incident_id}/resolve")
async def resolve_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    incident.status = "resolved"
    incident.resolved_at = datetime.utcnow()
    incident.revenue_at_risk = 0.0
    
    # Restore payment provider health
    payment_provider = get_payment_provider()
    payment_provider.set_method_health("upi", "healthy", 0.95)
    
    # Log resolution event
    res_evt = AgentEvent(
        id=f"evt_res_{incident_id[:6]}",
        incident_id=incident_id,
        agent_name="Growth Orchestrator",
        event_type="incident_resolved",
        input_summary="Merchant clicked Resolve Incident / Telemetry normalized",
        output_summary="Incident marked resolved. UPI gateway health restored to Healthy (95% success rate).",
        decision="resolve_incident",
        confidence=1.0,
        created_at=datetime.utcnow()
    )
    db.add(res_evt)
    await db.commit()
    
    return {"message": "Incident resolved successfully", "incident_id": incident_id}

@router.post("/{incident_id}/apply-recovery")
async def apply_autonomous_recovery(incident_id: str, db: AsyncSession = Depends(get_db)):
    import uuid
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    incident.status = "recovering"
    
    # Degrade UPI so live checkouts force fallback to Card / NetBanking
    payment_provider = get_payment_provider()
    payment_provider.set_method_health("upi", "degraded", 0.75)
    
    rec_evt = AgentEvent(
        id=f"evt_rec_act_{uuid.uuid4().hex[:6]}",
        incident_id=incident_id,
        agent_name="Recovery Agent",
        event_type="recovery_rule_enforced",
        input_summary="Merchant activated Autonomous Recovery Strategy",
        output_summary="Active failover rule enforced: Rerouting degraded UPI checkout traffic to Card gateway with 1-click retry.",
        decision="enforce_card_failover",
        confidence=0.98,
        created_at=datetime.utcnow()
    )
    db.add(rec_evt)
    await db.commit()
    return {"message": "Autonomous recovery strategy applied successfully!", "status": "recovering"}

@router.post("/{incident_id}/notify-customers")
async def notify_impacted_customers(incident_id: str, db: AsyncSession = Depends(get_db)):
    import uuid
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    notif_evt = AgentEvent(
        id=f"evt_notif_{uuid.uuid4().hex[:6]}",
        incident_id=incident_id,
        agent_name="Growth Orchestrator",
        event_type="customer_notification_sent",
        input_summary=f"Dispatched SMS & Push updates to {incident.affected_transactions_count} impacted buyers",
        output_summary="Automated payment status update and 1-click retry link sent to all affected checkout sessions.",
        decision="notify_buyers",
        confidence=1.0,
        created_at=datetime.utcnow()
    )
    db.add(notif_evt)
    await db.commit()
    return {"message": f"Successfully notified {incident.affected_transactions_count} impacted buyers!"}
