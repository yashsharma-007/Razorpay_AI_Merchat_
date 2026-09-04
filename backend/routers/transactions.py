from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.database import get_db
from backend.models import Transaction, Customer

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("")
async def list_transactions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Transaction).order_by(desc(Transaction.created_at)).limit(100))
    transactions = result.scalars().all()
    
    # Map customer details
    customers_res = await db.execute(select(Customer))
    customers = {c.id: c.name for c in customers_res.scalars().all()}
    
    response = []
    for tx in transactions:
        response.append({
            "id": tx.id,
            "external_id": tx.external_id or f"TXN{tx.id[-6:].upper()}",
            "customer_id": tx.customer_id,
            "customer_name": customers.get(tx.customer_id, "Rahul Sharma"),
            "order_id": tx.order_id,
            "amount": tx.amount,
            "currency": tx.currency,
            "payment_method": tx.payment_method.upper(),
            "status": tx.status,
            "failure_reason": tx.failure_reason,
            "attempt_number": tx.attempt_number,
            "is_recovered": tx.is_recovered,
            "recovery_method": tx.recovery_method.upper() if tx.recovery_method else None,
            "created_at": tx.created_at.isoformat()
        })
    return response
