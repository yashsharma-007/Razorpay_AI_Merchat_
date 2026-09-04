import hmac
import hashlib
import json
from backend.services.razorpay_bridge import RazorpayBridge

def test_razorpay_bridge():
    print("\n--- 1. TESTING HMAC-SHA256 WEBHOOK SIGNATURE VERIFICATION ---")
    secret = "whsec_test_secret_key_123"
    raw_payload = json.dumps({
        "event": "payment.failed",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_test_999",
                    "amount": 499900,
                    "currency": "INR",
                    "status": "failed",
                    "method": "upi",
                    "error_description": "HDFC Bank switch latency timeout"
                }
            }
        }
    }).encode("utf-8")

    # Generate valid signature
    valid_sig = hmac.new(secret.encode("utf-8"), raw_payload, hashlib.sha256).hexdigest()
    
    is_valid = RazorpayBridge.verify_webhook_signature(raw_payload, valid_sig, secret)
    is_invalid = RazorpayBridge.verify_webhook_signature(raw_payload, "invalid_sig_123", secret)
    
    print(f"Valid Signature Result: {is_valid} (Expected: True)")
    print(f"Invalid Signature Result: {is_invalid} (Expected: False)")

    print("\n--- 2. TESTING RAZORPAY API CLIENT (REST ENDPOINTS) ---")
    payments = RazorpayBridge.fetch_payments(limit=5)
    print("Fetch Payments Result:", json.dumps(payments, indent=2))

    refund = RazorpayBridge.create_refund("pay_test_999", amount_in_paise=499900)
    print("Create Refund Result:", json.dumps(refund, indent=2))

    health = RazorpayBridge.get_methods_health()
    print("Methods Health Result:", json.dumps(health, indent=2))

if __name__ == "__main__":
    test_razorpay_bridge()
