from fastapi import APIRouter,Depends,Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.trade_service import _get_coin
from app.database.database import get_db
from app.schemas.analytics import AnalyticsResponse
from app.services.analytical_service import get_analytics
from app.services.watchlist import add_coin,remove_coin
from app.auth.dependencies import get_current_user
import uuid
router=APIRouter(prefix="/analytics",tags=["Analytics"])

@router.get("/{symbol}",response_model=AnalyticsResponse)
async def analytics(
    symbol:str,
    interval:str=Query(default="1h"),
    db:AsyncSession=Depends(get_db),
):
    return await get_analytics(db,symbol,interval)

@router.post("/watchlist/add")
async def add_to_watchlist(
    symbol:str,
    db:AsyncSession=Depends(get_db),
    current_user=Depends(get_current_user)
):
    coin=await _get_coin(db,symbol)
    await add_coin(db,current_user.id,coin.id)
    return {"message": f"{symbol} added to watchlist"}

@router.delete("/watchlist/remove")
async def remove_from_watchlist(
    symbol:str,
    db:AsyncSession=Depends(get_db),
    current_user=Depends(get_current_user)
):
    coin=await _get_coin(db,symbol)
    await remove_coin(db,current_user.id,coin.id)
    return {"message": f"{symbol} removed from watchlist"}