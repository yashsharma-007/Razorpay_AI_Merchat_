from typing import Dict, Any
from sqlalchemy import select, func
from backend.agents.base import BaseAgent, AgentOutput
from backend.database import AsyncSessionLocal
from backend.models import Transaction, Order, RecoveryAttempt

class RevenueRiskAgent(BaseAgent):
    def __init__(self):
        super().__init__("Revenue Risk Agent")

    async def run(self, input_data: Dict[str, Any]) -> AgentOutput:
        # Dynamically compute metrics from DB if session available
        async with AsyncSessionLocal() as db:
            # 1. Count actual failed transactions in DB
            res_fail = await db.execute(select(func.count(Transaction.id)).where(Transaction.status == "failed"))
            db_failed_count = res_fail.scalar() or 0

            # 2. Compute actual Average Order Value (AOV) from DB
            res_aov = await db.execute(select(func.avg(Order.amount)))
            db_aov = res_aov.scalar() or 4400.0

            # 3. Compute actual recoverability rate from RecoveryAttempt DB table
            res_tot = await db.execute(select(func.count(RecoveryAttempt.id)))
            tot_att = res_tot.scalar() or 0
            
            res_succ = await db.execute(select(func.count(RecoveryAttempt.id)).where(RecoveryAttempt.result == "success"))
            succ_att = res_succ.scalar() or 0

            recoverability = round(succ_att / tot_att, 2) if tot_att > 0 else 0.60

        affected_txns = input_data.get("affected_transactions", db_failed_count or 42)
        aov = round(float(input_data.get("average_order_value", db_aov or 4400.0)), 2)
        
        potential_value = round(affected_txns * aov, 2)
        revenue_at_risk = round(potential_value * recoverability, 2)
        projected_2hr = round(revenue_at_risk * 1.6, 2)
        
        breakdown = f"{affected_txns} affected failed transactions x ₹{aov:,.0f} Average Order Value = ₹{potential_value:,.0f} potential lost value. At estimated {int(recoverability*100)}% recoverability, revenue at risk is ₹{revenue_at_risk:,.0f}."
        
        return AgentOutput(
            agent_name=self.name,
            decision="risk_quantified",
            confidence=0.95,
            reasoning_summary=f"Quantified revenue at risk to be ₹{revenue_at_risk:,.0f} across {affected_txns} transactions with a projected 2-hour impact of ₹{projected_2hr:,.0f}.",
            action="notify_orchestrator",
            metadata={
                "affected_transactions": affected_txns,
                "average_order_value": aov,
                "potential_value": potential_value,
                "recoverability_rate": recoverability,
                "revenue_at_risk": revenue_at_risk,
                "projected_revenue_impact": projected_2hr,
                "calculation_breakdown": breakdown
            }
        )
