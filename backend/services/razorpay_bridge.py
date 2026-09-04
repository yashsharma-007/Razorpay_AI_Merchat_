import hmac
import hashlib
import json
import base64
import urllib.request
import logging
from typing import Dict, Any, List, Optional
from backend.config import settings

logger = logging.getLogger(__name__)

class RazorpayBridge:
    """
    Production-Grade Drop-In Integration Bridge for Razorpay API.
    
    When deployed at Razorpay, simply set:
    RAZORPAY_API_BASE_URL=https://api.razorpay.com/v1 (or internal production gateway URI)
    RAZORPAY_KEY_ID=rzp_live_xxx
    RAZORPAY_KEY_SECRET=xxx
    RAZORPAY_WEBHOOK_SECRET=xxx
    RAZORPAY_MODE=live
    """
    
    @staticmethod
    def verify_webhook_signature(body_bytes: bytes, signature_header: str, secret: Optional[str] = None) -> bool:
        """
        Verifies official Razorpay HMAC-SHA256 signature from `x-razorpay-signature` header.
        """
        webhook_secret = secret or settings.RAZORPAY_WEBHOOK_SECRET
        if not webhook_secret or not signature_header:
            return True  # If no secret configured in test/demo mode, skip verification

        try:
            expected_signature = hmac.new(
                key=webhook_secret.encode("utf-8"),
                msg=body_bytes,
                digestmod=hashlib.sha256
            ).hexdigest()

            # Constant time string comparison to prevent timing attacks
            return hmac.compare_digest(expected_signature, signature_header)
        except Exception as e:
            logger.error(f"Error verifying Razorpay webhook signature: {str(e)}")
            return False

    @staticmethod
    def _make_live_request(endpoint: str, method: str = "GET", payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes HTTP requests to the Razorpay API using Basic Auth credentials.
        """
        url = f"{settings.RAZORPAY_API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
        auth_str = f"{settings.RAZORPAY_KEY_ID}:{settings.RAZORPAY_KEY_SECRET}"
        b64_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")

        headers = {
            "Authorization": f"Basic {b64_auth}",
            "Content-Type": "application/json",
            "User-Agent": "MerchantPulseAI-RazorpayBridge/1.0"
        }

        data_bytes = json.dumps(payload).encode("utf-8") if payload else None

        req = urllib.request.Request(
            url=url,
            data=data_bytes,
            headers=headers,
            method=method.upper()
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp_bytes = resp.read()
                return json.loads(resp_bytes.decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            logger.error(f"Razorpay API Error [{e.code}]: {error_body}")
            raise Exception(f"Razorpay API [{e.code}]: {error_body}")
        except Exception as e:
            logger.error(f"Razorpay API connection error: {str(e)}")
            raise e

    @classmethod
    def fetch_payments(cls, from_timestamp: Optional[int] = None, limit: int = 50) -> Dict[str, Any]:
        """
        Fetch live payments list from Razorpay API (/v1/payments).
        """
        if settings.RAZORPAY_MODE == "live":
            query_params = f"?count={limit}"
            if from_timestamp:
                query_params += f"&from={from_timestamp}"
            return cls._make_live_request(f"payments{query_params}", method="GET")
        else:
            # Fallback mock response for demo
            return {
                "entity": "collection",
                "count": 2,
                "items": [
                    {
                        "id": "pay_live_demo_101",
                        "entity": "payment",
                        "amount": 499900,
                        "currency": "INR",
                        "status": "failed",
                        "method": "upi",
                        "error_code": "BAD_REQUEST_PAYMENT_TIMED_OUT",
                        "error_description": "UPI Gateway response timed out after 15s"
                    },
                    {
                        "id": "pay_live_demo_102",
                        "entity": "payment",
                        "amount": 129900,
                        "currency": "INR",
                        "status": "captured",
                        "method": "card"
                    }
                ]
            }

    @classmethod
    def fetch_payment_by_id(cls, payment_id: str) -> Dict[str, Any]:
        """
        Fetch payment details by ID from Razorpay API (/v1/payments/{payment_id}).
        """
        if settings.RAZORPAY_MODE == "live":
            return cls._make_live_request(f"payments/{payment_id}", method="GET")
        else:
            return {
                "id": payment_id,
                "entity": "payment",
                "amount": 499900,
                "currency": "INR",
                "status": "failed",
                "method": "upi",
                "error_description": "HDFC UPI Bank Gateway Timeout"
            }

    @classmethod
    def create_refund(cls, payment_id: str, amount_in_paise: Optional[int] = None, notes: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Trigger an instant refund for a payment (/v1/payments/{payment_id}/refund).
        """
        payload = {}
        if amount_in_paise:
            payload["amount"] = amount_in_paise
        if notes:
            payload["notes"] = notes

        if settings.RAZORPAY_MODE == "live":
            return cls._make_live_request(f"payments/{payment_id}/refund", method="POST", payload=payload)
        else:
            return {
                "id": f"rfnd_{payment_id[:8]}",
                "entity": "refund",
                "payment_id": payment_id,
                "amount": amount_in_paise or 499900,
                "currency": "INR",
                "status": "processed",
                "notes": notes or {"reason": "Autonomous Recovery Refund"}
            }

    @classmethod
    def get_methods_health(cls) -> Dict[str, Any]:
        """
        Fetch live payment method availability & uptime from Razorpay API (/v1/methods).
        """
        if settings.RAZORPAY_MODE == "live":
            return cls._make_live_request("methods", method="GET")
        else:
            return {
                "entity": "methods",
                "upi": True,
                "card": True,
                "netbanking": True,
                "wallet": True
            }
