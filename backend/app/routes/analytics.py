from fastapi import APIRouter,Depends,Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.schemas.analytics import AnalyticsResponse
from app.services.analytical_service import get_analytics


router=APIRouter(prefix="/analytics",tags=["Analytics"])

@router.get("/{symbol}",response_model=AnalyticsResponse)
async def analytics(
    symbol:str,
    interval:str=Query(default="1h"),
    db:AsyncSession=Depends(get_db),
):
    return await get_analytics(db,symbol,interval)

