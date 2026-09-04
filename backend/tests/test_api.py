import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.database import init_db
from backend.seed_data import seed_database

@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    await init_db()
    await seed_database()
    yield

@pytest.mark.asyncio
async def test_root_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["project"] == "Merchant Pulse AI"

@pytest.mark.asyncio
async def test_dashboard_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "kpis" in data
        assert "growth_impact" in data
        assert "payment_health" in data

@pytest.mark.asyncio
async def test_low_rating_reviews_and_ai_summary():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Fetch low rating reviews < 4 stars
        res_low = await ac.get("/api/reviews/low-rating")
        assert res_low.status_code == 200
        reviews_low = res_low.json()
        assert len(reviews_low) > 0
        assert all(r["rating"] < 4 for r in reviews_low)

        # Fetch AI summary digest
        res_summary = await ac.get("/api/reviews/summary")
        assert res_summary.status_code == 200
        summary_data = res_summary.json()
        assert "executive_summary" in summary_data
        assert "top_recurring_pain_points" in summary_data
        assert "recommended_merchant_actions" in summary_data

@pytest.mark.asyncio
async def test_trigger_critical_email_alert():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        req_payload = {
            "review_text": "UPI payment failed twice, money deducted from my HDFC account!",
            "rating": 1,
            "customer_name": "Rahul Sharma",
            "merchant_email": "yss20042003@gmail.com"
        }
        res_email = await ac.post("/api/reviews/trigger-email-alert", json=req_payload)
        assert res_email.status_code == 200
        data = res_email.json()
        assert "Critical Warning Email Alert dispatched" in data["message"]

        # Fetch email alert logs
        res_logs = await ac.get("/api/reviews/email-alerts")
        assert res_logs.status_code == 200
        logs = res_logs.json()
        assert len(logs) > 0
        assert logs[0]["merchant_email"] == "yss20042003@gmail.com"

@pytest.mark.asyncio
async def test_simulate_incident():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/demo/simulate-incident", json={"reviews_count": 10})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "incident_id" in data
        assert data["revenue_at_risk"] > 0

@pytest.mark.asyncio
async def test_checkout_recovery_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # First simulate incident so UPI is degraded
        await ac.post("/api/demo/simulate-incident", json={"reviews_count": 5})

        # Process UPI payment attempt (expected to fail during degraded mode)
        req_body = {
            "order_id": "ord_test_101",
            "customer_id": "c_102",
            "product_id": "p_headphones",
            "amount": 4999.0,
            "payment_method": "upi",
            "is_retry": False
        }
        res_fail = await ac.post("/api/checkout/process", json=req_body)
        assert res_fail.status_code == 200
        data_fail = res_fail.json()
        assert data_fail["status"] == "failed"
        assert data_fail["recovery_recommendation"] is not None
        assert data_fail["recovery_recommendation"]["recommended_method"] == "card"

        # Process Recovery attempt switching to Card
        req_retry = {
            "order_id": "ord_test_101",
            "customer_id": "c_102",
            "product_id": "p_headphones",
            "amount": 4999.0,
            "payment_method": "card",
            "is_retry": True,
            "recovered_via": "card"
        }
        res_success = await ac.post("/api/checkout/process", json=req_retry)
        assert res_success.status_code == 200
        data_success = res_success.json()
        assert data_success["status"] == "success"
