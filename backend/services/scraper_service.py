import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.config import settings
from backend.database import AsyncSessionLocal
from backend.models import Review
from backend.providers.review_provider import get_review_provider
from backend.services.email_service import EmailAlertService
from backend.agents.orchestrator import growth_orchestrator

logger = logging.getLogger(__name__)

scraper_state = {
    "last_sync_time": None,
    "total_scraped": 0,
    "total_low_ratings": 0,
    "is_running": False
}

async def poll_and_ingest_playstore_reviews(db: AsyncSession, app_id: str = None, count: int = 50) -> Dict[str, Any]:
    target_app_id = app_id or settings.PLAYSTORE_APP_ID
    provider = get_review_provider(target_app_id)
    
    # 1. Fetch live payment-gateway related reviews from Play Store
    scraped_reviews = await provider.fetch_reviews(target_app_id, count=count)
    
    # 2. Get existing external review IDs to prevent duplicates
    existing_res = await db.execute(select(Review.external_review_id))
    existing_ids = set(r for r in existing_res.scalars().all() if r)
    
    new_reviews_added = []
    low_rating_added = []
    critical_alerts_triggered = []
    
    for r in scraped_reviews:
        ext_id = r.get("external_review_id", "")
        if ext_id and ext_id in existing_ids:
            continue
            
        rating = r.get("rating", 1)
        review_text = r.get("review_text", "")
        severity = r.get("severity", "high" if rating <= 2 else "medium")

        rev_id = f"rev_real_{uuid.uuid4().hex[:8]}"
        review_obj = Review(
            id=rev_id,
            external_review_id=ext_id or f"GP_{uuid.uuid4().hex[:6]}",
            customer_name=r.get("customer_name", "PlayStore User"),
            rating=rating,
            review_text=review_text,
            app_version=r.get("app_version", "v3.4.2"),
            device=r.get("device", "Android Device"),
            sentiment="negative" if rating <= 2 else ("neutral" if rating == 3 else "positive"),
            category="payment_failure",
            severity=severity,
            payment_related=True,
            processed=True,
            ai_confidence=0.96,
            created_at=datetime.utcnow()
        )
        db.add(review_obj)
        new_reviews_added.append(review_obj)
        
        if rating < 4:
            low_rating_added.append(review_obj)
            
        # Trigger Critical Warning Email Alert if rating <= 2 or critical
        if rating <= 2 or severity == "critical":
            email_alert = await EmailAlertService.send_critical_warning_email(
                merchant_email="ops@apexretail.in",
                subject=f"🚨 [CRITICAL PAYMENT GATEWAY WARNING] Low Rating ({rating}★) - {review_obj.customer_name}",
                review_text=review_text,
                rating=rating,
                severity=severity,
                customer_name=review_obj.customer_name,
                ai_summary=f"Customer review reports payment gateway failure on version {review_obj.app_version}.",
                action_recommended="Autonomous Recovery Agent active to route affected checkouts to Card."
            )
            critical_alerts_triggered.append(email_alert)

    await db.commit()
    
    # Update state
    scraper_state["last_sync_time"] = datetime.utcnow().isoformat()
    scraper_state["total_scraped"] += len(scraped_reviews)
    scraper_state["total_low_ratings"] += len(low_rating_added)
    
    # Trigger Orchestrator if critical payment reviews ingested
    if len(critical_alerts_triggered) > 0:
        reviews_dict_list = [
            {"review_text": r.review_text, "payment_related": True, "sentiment": r.sentiment, "rating": r.rating}
            for r in new_reviews_added
        ]
        await growth_orchestrator.run_full_incident_pipeline(
            db,
            reviews=reviews_dict_list,
            payment_events=[{"method": "upi", "status": "failed"}] * len(critical_alerts_triggered)
        )

    return {
        "new_reviews_count": len(new_reviews_added),
        "low_ratings_count": len(low_rating_added),
        "critical_alerts_count": len(critical_alerts_triggered),
        "app_id": target_app_id,
        "last_sync": scraper_state["last_sync_time"]
    }

async def run_periodic_playstore_scraper():
    scraper_state["is_running"] = True
    logger.info("Starting background Payment Play Store review scraping pipeline...")
    while True:
        try:
            async with AsyncSessionLocal() as db:
                await poll_and_ingest_playstore_reviews(db)
        except Exception as e:
            logger.error(f"Error in background payment scraper task: {str(e)}")
        await asyncio.sleep(60)
