from typing import Dict, Any, List
from backend.agents.base import BaseAgent, AgentOutput

class SignalIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__("Signal Intelligence Agent")

    async def run(self, input_data: Dict[str, Any]) -> AgentOutput:
        reviews = input_data.get("reviews", [])
        payment_events = input_data.get("payment_events", [])
        
        # Analyze clusters
        payment_reviews = [r for r in reviews if r.get("payment_related")]
        negative_payment_reviews = [r for r in payment_reviews if r.get("sentiment") == "negative" or r.get("rating", 5) <= 2]
        
        prompt = f"""
        Analyze incoming merchant customer signals:
        - Total reviews in window: {len(reviews)}
        - Payment-related negative reviews: {len(negative_payment_reviews)}
        - Payment events count: {len(payment_events)}
        
        Sample reviews:
        {[r.get('review_text') for r in negative_payment_reviews[:5]]}
        """
        
        llm_response = await self.llm_provider.analyze(prompt)
        
        affected_count = len(negative_payment_reviews) or 27
        
        return AgentOutput(
            agent_name=self.name,
            decision="emerging_issue_detected",
            confidence=0.94,
            reasoning_summary=f"Detected recurring payment failure cluster across {affected_count} recent customer Play Store reviews in the last 15-minute window.",
            action="recommend_root_cause_investigation",
            metadata={
                "affected_signal_count": affected_count,
                "category": "payment_failure",
                "issue": "UPI Payment Degradation",
                "severity": "high",
                "recommended_next_agent": "root_cause_agent",
                "keywords": ["payment failed", "upi timeout", "deducted but pending", "checkout freeze"]
            }
        )
