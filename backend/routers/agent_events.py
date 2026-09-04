from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.database import get_db
from backend.models import AgentEvent

router = APIRouter(prefix="/agent-events", tags=["agent-events"])

@router.get("")
async def list_agent_events(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgentEvent).order_by(desc(AgentEvent.created_at)).limit(100))
    events = result.scalars().all()
    return events
