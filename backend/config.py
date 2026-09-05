import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Merchant Pulse AI"
    API_V1_STR: str = "/api"
    AI_MODE: str = os.getenv("AI_MODE", "real")
    PAYMENT_MODE: str = os.getenv("PAYMENT_MODE", "mock")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    CREWAI_API_KEY: str = os.getenv("CREWAI_API_KEY", "")
    CREWAI_ORGANIZATION_ID: str = os.getenv("CREWAI_ORGANIZATION_ID", "")
    AGENTOPS_API_KEY: str = os.getenv("AGENTOPS_API_KEY", "")
    PLAYSTORE_APP_ID: str = os.getenv("PLAYSTORE_APP_ID", "com.razorpay.merchant")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./merchant_pulse.db")
    
    # SMTP / Gmail Credentials & Resend API Key for real inbox delivery
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")

    # Production Razorpay Integration Settings (Drop-In Ready)
    RAZORPAY_API_BASE_URL: str = os.getenv("RAZORPAY_API_BASE_URL", "https://api.razorpay.com/v1")
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "rzp_test_merchant_pulse")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "secret_merchant_pulse_key")
    RAZORPAY_WEBHOOK_SECRET: str = os.getenv("RAZORPAY_WEBHOOK_SECRET", "whsec_merchant_pulse_token")
    RAZORPAY_MODE: str = os.getenv("RAZORPAY_MODE", "mock")  # "live" or "mock"

    model_config = ConfigDict(case_sensitive=True)

settings = Settings()
