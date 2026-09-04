from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base

class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[str] = mapped_column(String, primary_key=True, default="m_default")
    name: Mapped[str] = mapped_column(String, default="Apex Retail India")
    email: Mapped[str] = mapped_column(String, default="ops@apexretail.in")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String, default="+919876543210")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String, default="INR")
    image_url: Mapped[str] = mapped_column(String, default="")
    stock: Mapped[int] = mapped_column(Integer, default=100)

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    customer_id: Mapped[str] = mapped_column(String, ForeignKey("customers.id"))
    product_id: Mapped[str] = mapped_column(String, ForeignKey("products.id"))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String, default="INR")
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, completed, failed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    external_id: Mapped[str] = mapped_column(String, default="")
    customer_id: Mapped[str] = mapped_column(String, ForeignKey("customers.id"))
    order_id: Mapped[str] = mapped_column(String, ForeignKey("orders.id"))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String, default="INR")
    payment_method: Mapped[str] = mapped_column(String)  # upi, card, netbanking, wallet
    status: Mapped[str] = mapped_column(String)  # success, failed, pending
    failure_reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    is_recovered: Mapped[bool] = mapped_column(Boolean, default=False)
    recovery_method: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    external_review_id: Mapped[str] = mapped_column(String, default="")
    customer_name: Mapped[str] = mapped_column(String, default="Anonymous Buyer")
    rating: Mapped[int] = mapped_column(Integer, default=1)
    review_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    app_version: Mapped[str] = mapped_column(String, default="v3.4.2")
    device: Mapped[str] = mapped_column(String, default="Android")
    language: Mapped[str] = mapped_column(String, default="en")
    sentiment: Mapped[str] = mapped_column(String, default="negative")
    category: Mapped[str] = mapped_column(String, default="payment_failure")
    severity: Mapped[str] = mapped_column(String, default="high")
    payment_related: Mapped[bool] = mapped_column(Boolean, default=True)
    processed: Mapped[bool] = mapped_column(Boolean, default=True)
    ai_confidence: Mapped[float] = mapped_column(Float, default=0.92)

class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    merchant_id: Mapped[str] = mapped_column(String, default="m_default")
    title: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String, default="payment")
    severity: Mapped[str] = mapped_column(String, default="critical")  # low, medium, high, critical
    status: Mapped[str] = mapped_column(String, default="active")  # active, recovering, resolved
    confidence: Mapped[float] = mapped_column(Float, default=0.93)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    affected_transactions_count: Mapped[int] = mapped_column(Integer, default=0)
    revenue_at_risk: Mapped[float] = mapped_column(Float, default=0.0)
    projected_revenue_impact: Mapped[float] = mapped_column(Float, default=0.0)
    root_cause: Mapped[str] = mapped_column(Text)
    evidence: Mapped[list] = mapped_column(JSON, default=list)
    ai_summary: Mapped[str] = mapped_column(Text)
    recommended_action: Mapped[str] = mapped_column(Text)
    mttd_seconds: Mapped[int] = mapped_column(Integer, default=161)  # Mean Time to Detect (2m 41s)

class AgentEvent(Base):
    __tablename__ = "agent_events"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    incident_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    agent_name: Mapped[str] = mapped_column(String)  # Signal, Root Cause, Risk, Orchestrator, Recovery
    event_type: Mapped[str] = mapped_column(String)
    input_summary: Mapped[str] = mapped_column(Text)
    output_summary: Mapped[str] = mapped_column(Text)
    decision: Mapped[str] = mapped_column(String)
    confidence: Mapped[float] = mapped_column(Float, default=0.90)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class RecoveryAttempt(Base):
    __tablename__ = "recovery_attempts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String, ForeignKey("transactions.id"))
    customer_id: Mapped[str] = mapped_column(String)
    original_method: Mapped[str] = mapped_column(String)
    failure_reason: Mapped[str] = mapped_column(String)
    strategy: Mapped[str] = mapped_column(String)  # SWITCH_PAYMENT_METHOD, RETRY_SAME_METHOD, etc.
    recommended_method: Mapped[str] = mapped_column(String)
    result: Mapped[str] = mapped_column(String)  # success, failed, abandoned
    recovered_amount: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class MerchantPolicy(Base):
    __tablename__ = "merchant_policy"

    id: Mapped[str] = mapped_column(String, primary_key=True, default="policy_default")
    auto_recovery_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    max_auto_recovery_amount: Mapped[float] = mapped_column(Float, default=50000.0)
    preferred_fallback_methods: Mapped[list] = mapped_column(JSON, default=lambda: ["card", "netbanking"])
    merchant_alert_threshold: Mapped[float] = mapped_column(Float, default=10000.0)

class RefundRecord(Base):
    __tablename__ = "refund_records"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String, ForeignKey("transactions.id"))
    customer_email: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float)
    reason: Mapped[str] = mapped_column(String, default="Bank Timeout Reconciliation")
    status: Mapped[str] = mapped_column(String, default="processed")  # processed, pending, failed
    razorpay_refund_id: Mapped[str] = mapped_column(String, default="")
    customer_notified: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
