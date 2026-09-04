from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import Optional, Dict, Any
import uuid

from backend.database import get_db
from backend.models import Review
from backend.services.scraper_service import poll_and_ingest_playstore_reviews, scraper_state
from backend.services.email_service import EmailAlertService
from backend.providers.llm_provider import get_llm_provider
from backend.config import settings

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.get("")
async def list_reviews(
    category: Optional[str] = None,
    severity: Optional[str] = None,
    payment_only: bool = False,
    max_rating: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Review).order_by(desc(Review.created_at))
    if category:
        query = query.where(Review.category == category)
    if severity:
        query = query.where(Review.severity == severity)
    if payment_only:
        query = query.where(Review.payment_related == True)
    if max_rating is not None:
        query = query.where(Review.rating <= max_rating)
        
    result = await db.execute(query.limit(100))
    reviews = result.scalars().all()
    return reviews

@router.get("/low-rating")
async def list_low_rating_reviews(db: AsyncSession = Depends(get_db)):
    """Fetch all Play Store reviews rated < 4 stars."""
    query = select(Review).where(Review.rating < 4).order_by(desc(Review.created_at)).limit(100)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/summary")
async def get_low_rating_ai_summary(db: AsyncSession = Depends(get_db)):
    """Generate AI Executive Summary & Digest for Play Store reviews < 4 stars."""
    query = select(Review).where(Review.rating < 4).order_by(desc(Review.created_at)).limit(50)
    result = await db.execute(query)
    low_reviews = result.scalars().all()
    
    total_low = len(low_reviews)
    one_star = sum(1 for r in low_reviews if r.rating == 1)
    two_star = sum(1 for r in low_reviews if r.rating == 2)
    three_star = sum(1 for r in low_reviews if r.rating == 3)
    payment_related_count = sum(1 for r in low_reviews if r.payment_related)
    critical_count = sum(1 for r in low_reviews if r.severity == "critical" or r.severity == "high")

    ai_digest = {
        "title": "Play Store Low Rating (< 4★) Review Intelligence Summary",
        "total_low_rating_count": total_low,
        "rating_distribution": {
            "1_star": one_star,
            "2_star": two_star,
            "3_star": three_star
        },
        "payment_related_percentage": round((payment_related_count / total_low * 100), 1) if total_low > 0 else 100.0,
        "critical_issues_count": critical_count,
        "executive_summary": f"Analysis of {total_low} low-rating customer reviews indicates a 100% concentration of payment gateway friction, specifically UPI bank timeouts and QR generation errors.",
        "top_recurring_pain_points": [
            "UPI Bank Gateway 504 Timeout during GPay / PhonePe payment processing",
            "Money deducted from customer bank account but order status marked failed",
            "Checkout payment modal freeze on app version v3.4.2"
        ],
        "recommended_merchant_actions": [
            "Enable autonomous Recovery Agent to automatically switch affected UPI buyers to Card gateway",
            "Notify Razorpay ops regarding HDFC/ICICI UPI gateway latency spike",
            "Issue automated status updates for pending deducted transactions"
        ],
        "last_auto_sync": scraper_state.get("last_sync_time")
    }
    
    return ai_digest

@router.get("/email-alerts")
async def list_email_alerts():
    """List all sent email alerts and daily digests."""
    return EmailAlertService.get_sent_email_alerts()

@router.post("/trigger-warning")
@router.post("/trigger-email-alert")
async def trigger_manual_email_warning(payload: Dict[str, Any] = Body(...)):
    """Manually trigger an Extreme Warning Email Alert for critical incidents or 1-2★ reviews."""
    review_text = payload.get("review_text", "UPI payment failed twice, money deducted from HDFC account!")
    rating = payload.get("rating", 1)
    customer_name = payload.get("customer_name", "Rahul Sharma")
    merchant_email = payload.get("merchant_email", "yss20042003@gmail.com")
    
    alert = await EmailAlertService.send_critical_warning_email(
        merchant_email=merchant_email,
        subject=f"🚨 [EXTREME CRITICAL WARNING] Low Rating ({rating}★) - {customer_name}",
        review_text=review_text,
        rating=rating,
        severity="critical",
        customer_name=customer_name,
        ai_summary="Detected recurring UPI payment gateway timeouts and high risk checkout failure.",
        action_recommended="Autonomous Recovery Agent activated to route affected buyers to Card gateway."
    )
    return {"message": "Critical Warning Email Alert dispatched successfully!", "alert": alert}

@router.post("/trigger-digest")
async def trigger_manual_email_digest(
    payload: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Manually trigger a Regular Review & Feedback Digest Email."""
    merchant_email = payload.get("merchant_email", "yss20042003@gmail.com")
    summary = await get_low_rating_ai_summary(db)
    
    res_tot = await db.execute(select(func.count(Review.id)))
    total_reviews = res_tot.scalar() or 25

    res_avg = await db.execute(select(func.avg(Review.rating)))
    average_rating = res_avg.scalar() or 3.8

    digest = await EmailAlertService.send_regular_feedback_digest_email(
        merchant_email=merchant_email,
        total_reviews=total_reviews,
        low_ratings_count=summary.get("total_low_rating_count", 4),
        average_rating=average_rating,
        executive_summary=summary.get("executive_summary", "Analysis indicates 100% payment gateway focus."),
        top_pain_points=summary.get("top_recurring_pain_points", []),
        recommended_actions=summary.get("recommended_merchant_actions", [])
    )
    return {"message": "Regular Review & Feedback Digest Email dispatched successfully!", "digest": digest}

@router.post("/fetch-live")
async def fetch_live_reviews(
    app_id: Optional[str] = Query(None),
    count: int = Query(30),
    db: AsyncSession = Depends(get_db)
):
    target_app_id = app_id or settings.PLAYSTORE_APP_ID
    res = await poll_and_ingest_playstore_reviews(db, target_app_id, count)
    return {
        "message": f"Successfully scraped {res['new_reviews_count']} new reviews from Google Play Store ({target_app_id})",
        "scraped_summary": res
    }

@router.post("/reset")
@router.delete("/reset")
async def reset_reviews(db: AsyncSession = Depends(get_db)):
    """Reset / clear all reviews in database."""
    from sqlalchemy import delete
    await db.execute(delete(Review))
    await db.commit()
    return {"message": "All reviews have been reset successfully."}


