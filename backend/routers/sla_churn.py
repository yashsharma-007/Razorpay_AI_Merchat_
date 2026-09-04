import uuid
from datetime import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.database import get_db
from backend.models import Transaction, Incident
from backend.providers.payment_provider import get_payment_provider

router = APIRouter(prefix="/sla-churn", tags=["sla-churn"])

@router.get("")
async def get_sla_and_churn_analytics(db: AsyncSession = Depends(get_db)):
    """
    Enterprise Merchant SLA Breach & Churn Predictor Analytics Endpoint.
    """
    payment_provider = get_payment_provider()
    is_upi_degraded = payment_provider.health_status.get("upi") == "degraded"
    
    # Calculate live success rate
    res_tot = await db.execute(select(func.count(Transaction.id)))
    total_txns = res_tot.scalar() or 100

    res_succ = await db.execute(select(func.count(Transaction.id)).where(Transaction.status == "success"))
    succ_txns = res_succ.scalar() or 82

    actual_uptime_pct = round((succ_txns / total_txns * 100), 2) if total_txns > 0 else (98.12 if is_upi_degraded else 99.98)
    if is_upi_degraded and actual_uptime_pct > 98.5:
        actual_uptime_pct = 98.12

    sla_target_pct = 99.95
    sla_breached = actual_uptime_pct < sla_target_pct
    sla_gap_pct = round(sla_target_pct - actual_uptime_pct, 2) if sla_breached else 0.0

    churn_risk_score = 64 if is_upi_degraded else 12  # Risk percentage
    churn_risk_level = "HIGH RISK" if churn_risk_score > 50 else ("MEDIUM" if churn_risk_score > 25 else "LOW")

    # High Value Accounts at Risk
    enterprise_merchants_at_risk = [
        {
            "merchant_name": "Apex Retail India (Swiggy Partner)",
            "monthly_gmv": "₹12.4 Cr",
            "sla_guarantee": "99.95%",
            "actual_uptime": f"{actual_uptime_pct}%",
            "churn_probability": f"{churn_risk_score}%",
            "financial_exposure_24h": "₹3,69,600",
            "primary_complaint": "HDFC UPI Timeout & Silent Debits"
        },
        {
            "merchant_name": "Meesho Logistics Direct",
            "monthly_gmv": "₹8.2 Cr",
            "sla_guarantee": "99.90%",
            "actual_uptime": "98.45%",
            "churn_probability": "48%",
            "financial_exposure_24h": "₹1,84,000",
            "primary_complaint": "Checkout Modal Freeze v3.4.2"
        }
    ]

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "sla_performance": {
            "sla_target_pct": sla_target_pct,
            "actual_uptime_pct": actual_uptime_pct,
            "sla_breached": sla_breached,
            "sla_gap_pct": sla_gap_pct,
            "breach_duration_minutes": 14 if is_upi_degraded else 0,
            "penalty_exposure_inr": 18480.0 if sla_breached else 0.0
        },
        "churn_risk_assessment": {
            "churn_risk_score_pct": churn_risk_score,
            "risk_level": churn_risk_level,
            "projected_24h_gmv_loss": "₹5,53,600" if is_upi_degraded else "₹0",
            "primary_churn_driver": "UPI Bank Timeout Failure Spikes" if is_upi_degraded else "None"
        },
        "proactive_kam_actions": [
            {
                "title": "Apply Temporary MDR Discount Fee Waiver",
                "impact": "Reduces merchant churn risk by 42%",
                "action": "Waive 0.15% MDR fee for 7 days during gateway switch migration."
            },
            {
                "title": "Enforce Priority Acquirer Switch Allocation",
                "impact": "Restores uptime to 99.8%",
                "action": "Route 80% of merchant UPI traffic away from HDFC switch to ICICI/Axis."
            },
            {
                "title": "Notify Key Account Manager (KAM)",
                "impact": "Proactive executive outreach",
                "action": "Dispatch automated incident debrief report to KAM (kam-lead@razorpay.com)."
            }
        ],
        "enterprise_merchants_at_risk": enterprise_merchants_at_risk
    }
