from typing import Dict, Any
from backend.agents.base import BaseAgent, AgentOutput

class RootCauseAgent(BaseAgent):
    def __init__(self):
        super().__init__("Root Cause Agent")

    async def run(self, input_data: Dict[str, Any]) -> AgentOutput:
        signal_summary = input_data.get("signal_summary", {})
        upi_failure_rate = input_data.get("upi_failure_rate", 13.7)
        baseline_failure_rate = input_data.get("baseline_failure_rate", 4.8)
        checkout_drop = input_data.get("checkout_conversion_drop", 8.4)
        
        evidence = [
            f"{signal_summary.get('affected_signal_count', 27)} customer Play Store reviews specifically report UPI payment failures",
            f"UPI failure rate spiked {round(upi_failure_rate / baseline_failure_rate, 1)}x (from {baseline_failure_rate}% to {upi_failure_rate}%)",
            f"Checkout conversion dropped {checkout_drop}% (from 74.1% to {round(74.1 - checkout_drop, 1)}%)",
            "Temporal correlation between Play Store review complaints and UPI bank gateway response timeout events (504 Gateway Timeout)"
        ]
        
        return AgentOutput(
            agent_name=self.name,
            decision="incident_confirmed",
            confidence=0.93,
            reasoning_summary="Strong correlation between customer review complaints and payment gateway telemetry confirms an active UPI degradation incident.",
            action="recommend_revenue_risk_assessment",
            metadata={
                "root_cause": "UPI Payment Degradation & Bank Gateway Timeout",
                "severity": "critical",
                "evidence": evidence,
                "impacted_method": "upi",
                "app_version": "v3.4.2"
            }
        )
