import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, Body, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional

from backend.database import get_db
from backend.models import Transaction, Order, Customer, Incident
from backend.agents.orchestrator import growth_orchestrator
from backend.providers.payment_provider import get_payment_provider

from fastapi import APIRouter, Depends, Body, Header, Request, HTTPException
from backend.services.razorpay_bridge import RazorpayBridge

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/payment")
@router.post("/razorpay")
async def handle_payment_webhook(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Real-time Razorpay & Gateway Payment Webhook Ingestion Endpoint.
    Validates HMAC-SHA256 signature when RAZORPAY_WEBHOOK_SECRET is configured.
    """
    body_bytes = await request.body()
    
    # 1. Signature Verification
    if x_razorpay_signature and not RazorpayBridge.verify_webhook_signature(body_bytes, x_razorpay_signature):
        logger.warning("❌ [INVALID RAZORPAY SIGNATURE] Rejected webhook request")
        raise HTTPException(status_code=400, detail="Invalid Razorpay Webhook Signature")

    try:
        payload = await request.json()
    except Exception:
        payload = {}
    event = payload.get("event", "payment.failed")
    
    if "payload" in payload and "payment" in payload["payload"]:
        p_entity = payload["payload"]["payment"]["entity"]
    else:
        p_entity = payload

    payment_id = p_entity.get("id", p_entity.get("payment_id", f"pay_{uuid.uuid4().hex[:8]}"))
    order_id = p_entity.get("order_id", f"ord_{uuid.uuid4().hex[:8]}")
    method = str(p_entity.get("method", "upi")).lower()
    
    raw_amount = float(p_entity.get("amount", 499900))
    amount = raw_amount / 100.0 if raw_amount > 1000 else raw_amount

    raw_status = str(p_entity.get("status", "failed")).lower()
    is_success = raw_status in ["captured", "authorized", "success", "completed"]
    status = "success" if is_success else "failed"

    failure_reason = p_entity.get("error_description") or p_entity.get("error_reason") or p_entity.get("failure_reason")
    if not is_success and not failure_reason:
        failure_reason = "bank_timeout" if method == "upi" else "issuer_bank_error"

    email = p_entity.get("email", "buyer@example.com")
    contact = p_entity.get("contact", "+919876543210")
    customer_name = email.split("@")[0].capitalize()

    # 1. Upsert Customer
    res_c = await db.execute(select(Customer).where(Customer.email == email))
    customer_obj = res_c.scalar_one_or_none()
    if not customer_obj:
        customer_obj = Customer(
            id=f"c_real_{uuid.uuid4().hex[:6]}",
            name=customer_name,
            email=email,
            phone=contact
        )
        db.add(customer_obj)
        await db.flush()

    # 2. Upsert Order
    res_o = await db.execute(select(Order).where(Order.id == order_id))
    order_obj = res_o.scalar_one_or_none()
    if not order_obj:
        order_obj = Order(
            id=order_id,
            customer_id=customer_obj.id,
            product_id="p_headphones",
            amount=amount,
            status="completed" if is_success else "failed",
            created_at=datetime.utcnow()
        )
        db.add(order_obj)
        await db.flush()

    # 3. Create Transaction
    txn = Transaction(
        id=f"txn_real_{uuid.uuid4().hex[:8]}",
        external_id=payment_id,
        customer_id=customer_obj.id,
        order_id=order_obj.id,
        amount=amount,
        currency="INR",
        payment_method=method,
        status=status,
        failure_reason=failure_reason if not is_success else None,
        attempt_number=1,
        is_recovered=False,
        created_at=datetime.utcnow()
    )
    db.add(txn)
    await db.commit()

    agent_summary = None
    if not is_success:
        payment_provider = get_payment_provider()
        if method == "upi":
            payment_provider.set_method_health("upi", "degraded", 0.82)
            
        pipeline_result = await growth_orchestrator.run_full_incident_pipeline(
            db,
            reviews=[],
            payment_events=[{"payment_id": payment_id, "method": method, "amount": amount, "reason": failure_reason}]
        )
        agent_summary = {
            "incident_id": pipeline_result["incident"].id,
            "revenue_at_risk": pipeline_result["incident"].revenue_at_risk,
            "root_cause": pipeline_result["incident"].root_cause
        }

    return {
        "status": "processed",
        "event": event,
        "payment_id": payment_id,
        "amount": amount,
        "method": method,
        "transaction_status": status,
        "telemetry_recorded": True,
        "agent_analysis": agent_summary
    }

@router.post("/n8n")
async def handle_n8n_agent_webhook(
    payload: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Dedicated Ingestion Endpoint for external n8n AI Agent workflows.
    Accepts n8n AI node outputs, runs backend orchestrator, and returns structured agent response to n8n.
    """
    review_text = payload.get("review_text", "UPI payment failure reported via n8n agent")
    rating = payload.get("rating", 1)
    payment_method = payload.get("payment_method", "upi")
    
    # Run full incident pipeline from n8n agent input
    pipeline_result = await growth_orchestrator.run_full_incident_pipeline(
        db,
        reviews=[{"review_text": review_text, "rating": rating, "payment_related": True}],
        payment_events=[{"method": payment_method, "status": "failed"}]
    )
    
    inc = pipeline_result["incident"]
    return {
        "source": "n8n_agentic_workflow",
        "status": "success",
        "incident_id": inc.id,
        "title": inc.title,
        "revenue_at_risk": inc.revenue_at_risk,
        "root_cause": inc.root_cause,
        "action_recommended": inc.recommended_action,
        "recovery_agent_status": "active"
    }
