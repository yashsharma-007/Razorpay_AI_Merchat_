from typing import Dict, Any
from backend.agents.base import BaseAgent, AgentOutput

class RecoveryAgent(BaseAgent):
    def __init__(self):
        super().__init__("Recovery Agent")

    async def run(self, input_data: Dict[str, Any]) -> AgentOutput:
        customer_id = input_data.get("customer_id", "C102")
        amount = input_data.get("amount", 4999.0)
        payment_method = input_data.get("payment_method", "upi").lower()
        failure_reason = input_data.get("failure_reason", "bank_timeout")
        attempt_count = input_data.get("attempt_count", 1)
        upi_degraded = input_data.get("upi_degraded", True)
        
        prompt = f"""
        Buyer recovery decision for checkout transaction:
        - Customer ID: {customer_id}
        - Amount: ₹{amount}
        - Failed Method: {payment_method}
        - Failure Reason: {failure_reason}
        - Attempt Count: {attempt_count}
        - Is UPI Degraded: {upi_degraded}
        
        Determine recovery strategy (SWITCH_PAYMENT_METHOD vs RETRY_SAME_METHOD) and user-facing message.
        """
        
        llm_response = await self.llm_provider.analyze(prompt)
        
        if payment_method == "upi" and upi_degraded:
            strategy = "SWITCH_PAYMENT_METHOD"
            recommended_method = "card"
            fallback_method = "netbanking"
            customer_message = f"Your UPI payment appears to be experiencing bank timeouts right now. Rather than retrying UPI, you can complete your ₹{amount:,.0f} payment instantly using Credit/Debit Card or Net Banking."
        else:
            strategy = "RETRY_SAME_METHOD"
            recommended_method = payment_method
            fallback_method = "card"
            customer_message = f"Payment retry initialized for ₹{amount:,.0f}."
            
        return AgentOutput(
            agent_name=self.name,
            decision=strategy,
            confidence=0.96,
            reasoning_summary=f"Selected {strategy} to guide buyer away from degraded {payment_method.upper()} toward healthy {recommended_method.upper()} gateway.",
            action="activate_buyer_intervention",
            metadata={
                "strategy": strategy,
                "recommended_method": recommended_method,
                "fallback_method": fallback_method,
                "customer_message": customer_message,
                "amount": amount,
                "customer_id": customer_id
            }
        )
