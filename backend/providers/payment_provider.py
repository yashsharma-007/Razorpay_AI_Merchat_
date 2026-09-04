import random
from typing import Dict, Any, List
from backend.config import settings

class PaymentProvider:
    def __init__(self):
        # Health state for payment methods
        # Default state
        self.health_status: Dict[str, str] = {
            "upi": "degraded",    # "healthy", "degraded", "down"
            "card": "healthy",
            "netbanking": "healthy",
            "wallet": "healthy"
        }
        self.success_rates: Dict[str, float] = {
            "upi": 0.82,          # degraded from 0.95
            "card": 0.96,
            "netbanking": 0.94,
            "wallet": 0.95
        }

    def set_method_health(self, method: str, status: str, success_rate: float):
        self.health_status[method] = status
        self.success_rates[method] = success_rate

    def get_health_status(self) -> Dict[str, Any]:
        is_upi_degraded = self.health_status.get("upi") == "degraded"
        return {
            "methods": [
                {
                    "name": "UPI",
                    "code": "upi",
                    "status": self.health_status.get("upi", "healthy"),
                    "success_rate": round(self.success_rates.get("upi", 0.95) * 100, 1),
                    "baseline_rate": 95.0,
                    "icon": "Smartphone"
                },
                {
                    "name": "Credit/Debit Card",
                    "code": "card",
                    "status": self.health_status.get("card", "healthy"),
                    "success_rate": round(self.success_rates.get("card", 0.96) * 100, 1),
                    "baseline_rate": 96.0,
                    "icon": "CreditCard"
                },
                {
                    "name": "Net Banking",
                    "code": "netbanking",
                    "status": self.health_status.get("netbanking", "healthy"),
                    "success_rate": round(self.success_rates.get("netbanking", 0.94) * 100, 1),
                    "baseline_rate": 94.0,
                    "icon": "Building"
                },
                {
                    "name": "Wallets",
                    "code": "wallet",
                    "status": self.health_status.get("wallet", "healthy"),
                    "success_rate": round(self.success_rates.get("wallet", 0.95) * 100, 1),
                    "baseline_rate": 95.0,
                    "icon": "Wallet"
                }
            ],
            "acquirers": [
                {
                    "bank": "HDFC Bank (UPI Switch)",
                    "code": "hdfc",
                    "status": "degraded" if is_upi_degraded else "healthy",
                    "latency_ms": 2450 if is_upi_degraded else 310,
                    "success_rate": 78.4 if is_upi_degraded else 96.2,
                    "recommended_traffic_pct": 10 if is_upi_degraded else 40
                },
                {
                    "bank": "ICICI Bank (UPI Switch)",
                    "code": "icici",
                    "status": "healthy",
                    "latency_ms": 280,
                    "success_rate": 97.1,
                    "recommended_traffic_pct": 50 if is_upi_degraded else 30
                },
                {
                    "bank": "Axis Bank (UPI Switch)",
                    "code": "axis",
                    "status": "healthy",
                    "latency_ms": 320,
                    "success_rate": 95.8,
                    "recommended_traffic_pct": 30 if is_upi_degraded else 20
                },
                {
                    "bank": "State Bank of India (SBI)",
                    "code": "sbi",
                    "status": "healthy",
                    "latency_ms": 410,
                    "success_rate": 94.5,
                    "recommended_traffic_pct": 10
                }
            ]
        }

    def process_payment(self, method: str, amount: float) -> Dict[str, Any]:
        method = method.lower()
        success_prob = self.success_rates.get(method, 0.90)
        
        # Deterministic override during degraded mode for UPI demo
        if method == "upi" and self.health_status.get("upi") == "degraded":
            is_success = False
            failure_reason = "bank_timeout"
        else:
            is_success = random.random() < success_prob
            failure_reason = None if is_success else "issuer_bank_error"

        return {
            "success": is_success,
            "payment_method": method,
            "amount": amount,
            "status": "success" if is_success else "failed",
            "failure_reason": failure_reason,
            "gateway_message": "Transaction completed successfully" if is_success else "UPI Bank Gateway response timed out after 15s"
        }

# Global payment provider instance
payment_provider_instance = PaymentProvider()

def get_payment_provider() -> PaymentProvider:
    return payment_provider_instance
