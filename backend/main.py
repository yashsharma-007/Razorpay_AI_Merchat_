import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.config import settings
import backend.models  # Register all SQLAlchemy models in Base.metadata
from backend.database import init_db
from backend.seed_data import seed_database
from backend.services.scraper_service import run_periodic_playstore_scraper
from backend.routers import (
    dashboard, incidents, transactions, reviews, recovery,
    agent_events, checkout, demo, settings as settings_router, webhooks, external_agents,
    refunds, sla_churn
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database & Seed initial data
    await init_db()
    await seed_database()
    
    # Start background Play Store scraper task
    scraper_task = asyncio.create_task(run_periodic_playstore_scraper())
    yield
    # Shutdown: Cancel background scraper task
    scraper_task.cancel()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(incidents.router, prefix=settings.API_V1_STR)
app.include_router(transactions.router, prefix=settings.API_V1_STR)
app.include_router(reviews.router, prefix=settings.API_V1_STR)
app.include_router(recovery.router, prefix=settings.API_V1_STR)
app.include_router(agent_events.router, prefix=settings.API_V1_STR)
app.include_router(checkout.router, prefix=settings.API_V1_STR)
app.include_router(demo.router, prefix=settings.API_V1_STR)
app.include_router(settings_router.router, prefix=settings.API_V1_STR)
app.include_router(webhooks.router, prefix=settings.API_V1_STR)
app.include_router(external_agents.router, prefix=settings.API_V1_STR)
app.include_router(refunds.router, prefix=settings.API_V1_STR)
app.include_router(sla_churn.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "tagline": "From customer signal to recovered revenue.",
        "status": "online",
        "ai_mode": settings.AI_MODE,
        "payment_mode": settings.PAYMENT_MODE
    }
