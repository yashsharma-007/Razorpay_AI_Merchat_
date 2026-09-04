import asyncio
import json
import logging
from backend.services.email_service import EmailAlertService

logging.basicConfig(level=logging.INFO)

async def run_email_test():
    print("\n--- TRIGGERING HIGH-END EXTREME CRITICAL WARNING EMAIL ---")
    warn_res = await EmailAlertService.send_critical_warning_email(
        merchant_email="yss20042003@gmail.com",
        subject="[CRITICAL ALERT] UPI Payment Gateway Timeout & Revenue Risk Spike",
        review_text="Money deducted from my HDFC account ₹4,999 but order failed! Payment modal stuck on loading loop.",
        rating=1,
        severity="critical",
        customer_name="Ananya Roy",
        ai_summary="Anomalous spike in UPI Autopay gateway 504 gateway timeouts correlated with HDFC Bank NPCI switch degradation. 42 transactions impacted in last 5 minutes.",
        action_recommended="Autonomous Agent initiated failover to Card / NetBanking gateway. Suppressed faulty UPI option on checkout UI for affected app users.",
        estimated_revenue_at_risk="₹2,10,000",
        affected_checkouts="48 Checkouts",
        mttd="1m 45s",
        failure_vector="HDFC UPI Gateway Timeout"
    )
    print("Warning Email Result:", json.dumps(warn_res, indent=2))

    print("\n--- TRIGGERING HIGH-END REGULAR FEEDBACK DIGEST EMAIL ---")
    digest_res = await EmailAlertService.send_regular_feedback_digest_email(
        merchant_email="yss20042003@gmail.com",
        total_reviews=1240,
        low_ratings_count=14,
        average_rating=4.6,
        executive_summary="Play Store customer sentiment remains overwhelmingly positive (4.6★ CSAT). Payment friction accounts for 85% of total 1-star complaints, specifically regarding delayed refund SMS notifications.",
        top_pain_points=[
            "Delayed SMS receipt after UPI deduction retry",
            "Checkout payment modal freeze on Android 14 app version v3.4.2",
            "Slow refund processing for cancelled COD orders"
        ],
        recommended_actions=[
            "Deploy automated WhatsApp status webhook for pending UPI transactions",
            "Push app hotfix v3.4.3 fixing payment webview initialization",
            "Enable autonomous instant refund routing via Razorpay Instant Refunds"
        ]
    )
    print("Digest Email Result:", json.dumps(digest_res, indent=2))

if __name__ == "__main__":
    asyncio.run(run_email_test())
