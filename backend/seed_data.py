import asyncio
import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy import select, delete

from backend.database import AsyncSessionLocal, init_db
from backend.models import (
    Merchant, Customer, Product, Order, Transaction, Review, Incident, AgentEvent, RecoveryAttempt, MerchantPolicy
)

async def seed_database(force: bool = False):
    await init_db()
    
    async with AsyncSessionLocal() as db:
        res = await db.get(Merchant, "m_default")
        if res and not force:
            print("Database already populated with realistic telemetry.")
            return

        if force:
            # Clear old tables
            for model in [Merchant, Customer, Product, Order, Transaction, Review, Incident, AgentEvent, RecoveryAttempt, MerchantPolicy]:
                await db.execute(delete(model))
            await db.commit()

        # 1. Seed Merchant & Policy
        merchant = Merchant(id="m_default", name="Apex Retail India", email="ops@apexretail.in")
        policy = MerchantPolicy(
            id="policy_default",
            auto_recovery_enabled=True,
            max_auto_recovery_amount=50000.0,
            preferred_fallback_methods=["card", "netbanking"],
            merchant_alert_threshold=10000.0
        )
        db.add(merchant)
        db.add(policy)

        # 2. Seed Products
        products_data = [
            ("p_headphones", "Premium Wireless Headphones", "Active Noise-Cancelling Headphones", 4999.0, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&auto=format&fit=crop&q=60"),
            ("p_smartwatch", "Pro Fitness Smartwatch", "AMOLED display with heart rate and SpO2 tracking", 7999.0, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&auto=format&fit=crop&q=60"),
            ("p_earbuds", "True Wireless Earbuds", "Spatial audio with active noise cancellation", 2999.0, "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&auto=format&fit=crop&q=60"),
            ("p_speaker", "Portable Bluetooth Speaker", "360-degree bass sound with IPX7 rating", 3499.0, "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=500&auto=format&fit=crop&q=60")
        ]
        products = []
        for pid, name, desc, price, img in products_data:
            p = Product(id=pid, name=name, description=desc, price=price, currency="INR", image_url=img, stock=100)
            db.add(p)
            products.append(p)

        # 3. Seed Customers (30 realistic customers)
        first_names = ["Rahul", "Priya", "Ananya", "Vikram", "Neha", "Rohan", "Siddharth", "Kavya", "Amit", "Pooja", "Arjun", "Sneha", "Aditya", "Riya", "Manish"]
        last_names = ["Sharma", "Patel", "Verma", "Singh", "Gupta", "Kumar", "Joshi", "Mehta", "Reddy", "Nair", "Chopra", "Deshmukh", "Iyer", "Rao", "Bhat"]
        
        customers = []
        for i in range(30):
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            cid = f"c_{i+101}"
            c = Customer(
                id=cid,
                name=f"{fn} {ln}",
                email=f"{fn.lower()}.{ln.lower()}{i}@example.com",
                phone=f"+9198{random.randint(10000000, 99999999)}"
            )
            db.add(c)
            customers.append(c)

        now = datetime.utcnow()

        # 4. Generate 120 Transactions across past 24 hours
        methods = ["upi", "card", "netbanking", "wallet"]
        method_weights = [0.55, 0.25, 0.12, 0.08]
        
        for i in range(120):
            tx_time = now - timedelta(minutes=random.randint(5, 1440))
            cust = random.choice(customers)
            prod = random.choice(products)
            method = random.choices(methods, weights=method_weights)[0]
            
            # Realistic success rates: UPI 92%, Card 96%, Netbanking 94%, Wallet 95%
            is_success = random.random() < (0.92 if method == "upi" else 0.95)
            status = "success" if is_success else "failed"
            reason = None if is_success else ("bank_timeout" if method == "upi" else "issuer_bank_error")
            
            oid = f"ord_{i+5000}"
            o = Order(
                id=oid,
                customer_id=cust.id,
                product_id=prod.id,
                amount=prod.price,
                status="completed" if is_success else "failed",
                created_at=tx_time
            )
            db.add(o)

            # Is this transaction a baseline recovered transaction?
            is_recovered = False
            rec_method = None
            if not is_success and random.random() < 0.65:
                # Recovered via Card or Netbanking
                is_recovered = True
                rec_method = "card" if random.random() < 0.75 else "netbanking"
                status = "success"
                reason = None
                o.status = "completed"

            t = Transaction(
                id=f"txn_{uuid.uuid4().hex[:8]}",
                external_id=f"TXN{random.randint(100000, 999999)}",
                customer_id=cust.id,
                order_id=oid,
                amount=prod.price,
                payment_method=method if not is_recovered else rec_method,
                status=status,
                failure_reason=reason,
                attempt_number=2 if is_recovered else 1,
                is_recovered=is_recovered,
                recovery_method=rec_method,
                created_at=tx_time
            )
            db.add(t)

            # Record Recovery Attempt if recovered
            if is_recovered:
                rec = RecoveryAttempt(
                    id=f"rec_{uuid.uuid4().hex[:8]}",
                    transaction_id=t.id,
                    customer_id=cust.id,
                    original_method="upi",
                    failure_reason="bank_timeout",
                    strategy="SWITCH_PAYMENT_METHOD",
                    recommended_method=rec_method,
                    result="success",
                    recovered_amount=prod.price,
                    created_at=tx_time
                )
                db.add(rec)

        # 5. Seed Realistic Play Store Reviews (25 reviews)
        sample_reviews_data = [
            ("UPI payment failed twice, money deducted from HDFC account but order failed!", 1, "payment_failure", "critical", True),
            ("Checkout freezes when choosing GPay. Please fix this bug asap.", 1, "checkout_abandonment", "high", True),
            ("Payment deduction happened twice for single order. Frustrating experience.", 1, "payment_failure", "critical", True),
            ("Unable to complete payment via PhonePe QR. Bank timeout error 504.", 2, "payment_failure", "high", True),
            ("App is good but payment gateway failed 3 times today morning.", 2, "payment_failure", "medium", True),
            ("Switched to Credit Card and payment went through instantly.", 3, "payment_failure", "medium", True),
            ("Excellent noise cancellation on headphones! Super fast delivery.", 5, "product_quality", "low", False),
            ("Clean UI design and smooth product navigation.", 4, "ui_experience", "low", False),
            ("UPI payment server error during checkout process.", 2, "payment_failure", "high", True),
            ("Order cancelled automatically after UPI transaction timeout.", 1, "payment_failure", "high", True)
        ]

        for idx in range(25):
            text, rating, cat, sev, pay_rel = sample_reviews_data[idx % len(sample_reviews_data)]
            rev_time = now - timedelta(minutes=random.randint(10, 720))
            r = Review(
                id=f"rev_seed_{idx+100}",
                external_review_id=f"GP900{idx+100}",
                customer_name=f"{random.choice(first_names)} {random.choice(last_names)}",
                rating=rating,
                review_text=f"{text} (Ref #{idx+1})",
                created_at=rev_time,
                app_version="v3.4.2",
                device="Android Device",
                sentiment="negative" if rating <= 2 else ("neutral" if rating == 3 else "positive"),
                category=cat,
                severity=sev,
                payment_related=pay_rel,
                processed=True,
                ai_confidence=0.94
            )
            db.add(r)

        await db.commit()
        print("Successfully populated database with 100+ realistic telemetry rows!")

if __name__ == "__main__":
    asyncio.run(seed_database(force=True))
