from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db
from backend.models import MerchantPolicy
from backend.schemas import MerchantPolicySchema

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("")
async def get_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MerchantPolicy).where(MerchantPolicy.id == "policy_default"))
    policy = result.scalar_one_or_none()
    if not policy:
        policy = MerchantPolicy(
            id="policy_default",
            auto_recovery_enabled=True,
            max_auto_recovery_amount=50000.0,
            preferred_fallback_methods=["card", "netbanking"],
            merchant_alert_threshold=10000.0
        )
        db.add(policy)
        await db.commit()
        await db.refresh(policy)
    return policy

@router.post("")
async def update_settings(req: MerchantPolicySchema, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MerchantPolicy).where(MerchantPolicy.id == "policy_default"))
    policy = result.scalar_one_or_none()
    if not policy:
        policy = MerchantPolicy(id="policy_default")
        db.add(policy)
        
    policy.auto_recovery_enabled = req.auto_recovery_enabled
    policy.max_auto_recovery_amount = req.max_auto_recovery_amount
    policy.preferred_fallback_methods = req.preferred_fallback_methods
    policy.merchant_alert_threshold = req.merchant_alert_threshold
    
    await db.commit()
    await db.refresh(policy)
    return policy
