import asyncio
import json
import logging
from backend.database import init_db, AsyncSessionLocal
from backend.agents.orchestrator import growth_orchestrator
from backend.providers.payment_provider import get_payment_provider

logging.basicConfig(level=logging.INFO)

async def test_live_incident():
    print("\n--- 1. INITIALIZING DATABASE & SIMULATING LIVE INCIDENT STREAM ---")
    await init_db()
    
    # Degrade UPI Gateway Health
    payment_provider = get_payment_provider()
    payment_provider.set_method_health("upi", "degraded", 0.82)
    print("UPI Payment Gateway Health set to DEGRADED (82% success rate)")

    sample_reviews = [
        {
            "customer_name": "Vikram Sethi",
            "rating": 1,
            "review_text": "GPay UPI transaction failed twice on checkout! Money deducted from my Axis Bank account but order shows pending!",
            "app_version": "v3.4.2",
            "device": "Samsung S23",
            "sentiment": "negative",
            "category": "payment_failure",
            "severity": "critical",
            "payment_related": True
        }
    ]

    payment_events = [{"method": "upi", "status": "failed", "reason": "bank_timeout"}] * 42

    async with AsyncSessionLocal() as db:
        print("\n--- 2. RUNNING MULTI-AGENT INCIDENT PIPELINE ---")
        result = await growth_orchestrator.run_full_incident_pipeline(
            db,
            reviews=sample_reviews,
            payment_events=payment_events
        )
        
        inc = result["incident"]
        print(f"\n--- 3. INCIDENT CREATED SUCCESSFULLY ---")
        print(f"Incident ID: {inc.id}")
        print(f"Title: {inc.title}")
        print(f"Severity: {inc.severity}")
        print(f"Status: {inc.status}")
        print(f"Revenue at Risk: ₹{inc.revenue_at_risk:,.0f}")
        print(f"MTTD: {inc.mttd_seconds}s (2m 41s)")
        print(f"Root Cause: {inc.root_cause}")
        print(f"Recommended Action: {inc.recommended_action}")
        print("\nCHECK YOUR INBOX (yss20042003@gmail.com) FOR THE AUTO-DISPATCHED EXTREME WARNING EMAIL!")

if __name__ == "__main__":
    asyncio.run(test_live_incident())
