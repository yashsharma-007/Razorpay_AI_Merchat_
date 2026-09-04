import asyncio
import json
from backend.database import init_db, AsyncSessionLocal
from backend.routers.refunds import trigger_auto_refund_reconciliation
from backend.routers.sla_churn import get_sla_and_churn_analytics

async def test_new_features():
    print("\n--- 1. INITIALIZING DATABASE ---")
    await init_db()

    async with AsyncSessionLocal() as db:
        print("\n--- 2. TESTING AUTONOMOUS INSTANT REFUND & DISPUTE GUARDIAN ---")
        refund_res = await trigger_auto_refund_reconciliation(payload={}, db=db)
        print("Refund Result:", json.dumps(refund_res, indent=2))

        print("\n--- 3. TESTING ENTERPRISE SLA BREACH & CHURN PREDICTOR ---")
        sla_res = await get_sla_and_churn_analytics(db=db)
        print("SLA & Churn Analytics Result:", json.dumps(sla_res, indent=2))

if __name__ == "__main__":
    asyncio.run(test_new_features())
