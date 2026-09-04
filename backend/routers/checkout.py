import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.database import get_db
from backend.models import Transaction, Order, Product, Customer, RecoveryAttempt, AgentEvent, Incident
from backend.schemas import ProcessPaymentRequest
from backend.providers.payment_provider import get_payment_provider
from backend.agents.recovery_agent import RecoveryAgent

router = APIRouter(prefix="/checkout", tags=["checkout"])

@router.get("/products")
async def get_checkout_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return products

@router.post("/process")
async def process_checkout_payment(req: ProcessPaymentRequest, db: AsyncSession = Depends(get_db)):
    payment_provider = get_payment_provider()
    
    # Process payment attempt
    pay_res = payment_provider.process_payment(req.payment_method, req.amount)
    
    txn_id = f"txn_{uuid.uuid4().hex[:8]}"
    is_success = pay_res["success"]
    
    # Is this a recovered transaction via AI guidance?
    is_recovered = req.is_retry and is_success and req.recovered_via is not None
    
    txn = Transaction(
        id=txn_id,
        external_id=f"TXN{uuid.uuid4().hex[:6].upper()}",
        customer_id=req.customer_id,
        order_id=req.order_id,
        amount=req.amount,
        currency="INR",
        payment_method=req.payment_method,
        status="success" if is_success else "failed",
        failure_reason=pay_res.get("failure_reason"),
        attempt_number=2 if req.is_retry else 1,
        is_recovered=is_recovered,
        recovery_method=req.recovered_via if is_recovered else None,
        created_at=datetime.utcnow()
    )
    db.add(txn)
    
    # Log recovery attempt if this was a recovery action
    if req.is_retry:
        rec_attempt = RecoveryAttempt(
            id=f"rec_{uuid.uuid4().hex[:8]}",
            transaction_id=txn_id,
            customer_id=req.customer_id,
            original_method="upi",
            failure_reason="bank_timeout",
            strategy="SWITCH_PAYMENT_METHOD" if req.recovered_via else "RETRY_SAME_METHOD",
            recommended_method=req.payment_method,
            result="success" if is_success else "failed",
            recovered_amount=req.amount if is_success else 0.0,
            created_at=datetime.utcnow()
        )
        db.add(rec_attempt)
        
        # Log Agent Event
        if is_success:
            evt = AgentEvent(
                id=f"evt_rec_{uuid.uuid4().hex[:8]}",
                incident_id=None,
                agent_name="Recovery Agent",
                event_type="payment_recovered",
                input_summary=f"Buyer switched from UPI to {req.payment_method.upper()} for order {req.order_id}",
                output_summary=f"Successfully recovered ₹{req.amount:,.0f} transaction! Merchant revenue updated.",
                decision="recovery_successful",
                confidence=1.0,
                created_at=datetime.utcnow()
            )
            db.add(evt)

    await db.commit()
    
    # If payment failed, call Recovery Agent to generate context-aware intervention
    recovery_recommendation = None
    if not is_success:
        recovery_agent = RecoveryAgent()
        health = payment_provider.get_health_status()
        upi_degraded = payment_provider.health_status.get("upi") == "degraded"
        
        agent_output = await recovery_agent.run({
            "customer_id": req.customer_id,
            "amount": req.amount,
            "payment_method": req.payment_method,
            "failure_reason": pay_res.get("failure_reason", "bank_timeout"),
            "attempt_count": 1,
            "upi_degraded": upi_degraded
        })
        
        recovery_recommendation = {
            "strategy": agent_output.metadata.get("strategy", "SWITCH_PAYMENT_METHOD"),
            "recommended_method": agent_output.metadata.get("recommended_method", "card"),
            "customer_message": agent_output.metadata.get("customer_message"),
            "available_healthy_methods": [m for m in health["methods"] if m["status"] == "healthy"],
            "reasoning_summary": agent_output.reasoning_summary
        }
        
    return {
        "transaction_id": txn_id,
        "status": "success" if is_success else "failed",
        "payment_method": req.payment_method,
        "gateway_message": pay_res["gateway_message"],
        "failure_reason": pay_res.get("failure_reason"),
        "recovery_recommendation": recovery_recommendation
    }
