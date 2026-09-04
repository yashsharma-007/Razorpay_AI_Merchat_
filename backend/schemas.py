from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class MerchantPolicySchema(BaseModel):
    auto_recovery_enabled: bool = True
    max_auto_recovery_amount: float = 50000.0
    preferred_fallback_methods: List[str] = ["card", "netbanking"]
    merchant_alert_threshold: float = 10000.0

class SimulateIncidentRequest(BaseModel):
    app_id: Optional[str] = "com.razorpay.merchant"
    reviews_count: Optional[int] = 25

class ProcessPaymentRequest(BaseModel):
    order_id: str
    customer_id: str
    product_id: str
    amount: float
    payment_method: str
    is_retry: bool = False
    recovered_via: Optional[str] = None

class SetHealthRequest(BaseModel):
    method: str
    status: str
    success_rate: float
