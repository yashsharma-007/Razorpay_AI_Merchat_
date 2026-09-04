import json
import httpx
from typing import Dict, Any, Optional
from backend.config import settings

class LLMProvider:
    async def analyze(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        raise NotImplementedError

class MockLLMProvider(LLMProvider):
    async def analyze(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        
        if "signal intelligence" in prompt_lower or "review analysis" in prompt_lower:
            return {
                "event_type": "emerging_issue",
                "category": "payment_failure",
                "issue": "UPI Payment Degradation",
                "severity": "high",
                "confidence": 0.94,
                "affected_signal_count": 27,
                "summary": "27 negative customer reviews detect recurring UPI transaction failures and checkout drops.",
                "keywords": ["payment failed", "upi timeout", "deducted but pending", "checkout freeze"]
            }
        
        elif "root cause" in prompt_lower:
            return {
                "root_cause": "UPI Bank Gateway Degradation",
                "confidence": 0.93,
                "evidence": [
                    "27 payment-related Play Store reviews in last 15 mins",
                    "UPI payment failure rate increased 2.85x (4.8% -> 13.7%)",
                    "Checkout conversion rate dropped 8.4% (74.1% -> 65.7%)"
                ],
                "severity": "critical",
                "impacted_method": "upi",
                "app_version_affected": "v3.4.2"
            }
            
        elif "revenue risk" in prompt_lower:
            return {
                "affected_transactions": 42,
                "average_order_value": 4400,
                "potential_loss": 184800,
                "estimated_recoverability": 0.60,
                "revenue_at_risk": 110880,
                "projected_2hr_impact": 180000,
                "calculation_breakdown": "42 failed checkouts x ₹4,400 AOV x (1 - 0.40 historical abandon rate) = ₹1,10,880 at risk."
            }
            
        elif "recovery strategy" in prompt_lower or "buyer recovery" in prompt_lower:
            return {
                "strategy": "SWITCH_PAYMENT_METHOD",
                "recommended_method": "card",
                "fallback_method": "netbanking",
                "reasoning_summary": "UPI is currently experiencing high failure rates (13.7%). Customer attempted UPI twice without success. Recommend switching to healthy Card gateway.",
                "customer_message": "Your UPI payment appears to be experiencing an issue right now. Rather than retrying UPI, you can complete your ₹4,999 payment seamlessly using Card.",
                "confidence": 0.96
            }
            
        else:
            return {
                "decision": "proceed",
                "confidence": 0.90,
                "reasoning_summary": "General analysis completed with baseline parameters.",
                "action": "log_telemetry"
            }

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def analyze(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.api_key:
            return await MockLLMProvider().analyze(prompt, schema)
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are Merchant Pulse AI Agent. Return valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"}
                },
                timeout=15.0
            )
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)

class GeminiLLMProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def analyze(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.api_key:
            return await MockLLMProvider().analyze(prompt, schema)
            
        async with httpx.AsyncClient() as client:
            for model_name in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
                try:
                    response = await client.post(
                        url,
                        json={
                            "contents": [{"parts": [{"text": f"You are Merchant Pulse AI Agent. Return valid JSON object only.\n\n{prompt}"}]}],
                            "generationConfig": {"responseMimeType": "application/json"}
                        },
                        timeout=10.0
                    )
                    data = response.json()
                    content = data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(content)
                except Exception:
                    continue
            return await MockLLMProvider().analyze(prompt, schema)

def get_llm_provider() -> LLMProvider:
    if settings.GEMINI_API_KEY:
        return GeminiLLMProvider(settings.GEMINI_API_KEY)
    elif settings.OPENAI_API_KEY:
        return OpenAIProvider(settings.OPENAI_API_KEY)
    return MockLLMProvider()
