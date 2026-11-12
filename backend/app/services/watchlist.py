from sqlalchemy.ext.asyncio import AsyncSession
from app.models.WatchList import WatchList
import uuid
from sqlalchemy import select

async def add_coin(db:AsyncSession,user_id:uuid.UUID,coin_id:uuid.UUID):
    
    new_watchlist_entry = WatchList(user_id=user_id, coin_id=coin_id)
    query=select(WatchList).where((WatchList.user_id==user_id)&(WatchList.coin_id==coin_id))
    existing_entry=(await db.execute(query)).scalar_one_or_none()
    if not existing_entry:
        db.add(new_watchlist_entry)
        await db.commit()
        await db.refresh(new_watchlist_entry)

async def remove_coin(db:AsyncSession,user_id:uuid.UUID,coin_id:uuid.UUID):
    query=select(WatchList).where((WatchList.user_id==user_id)&(WatchList.coin_id==coin_id))
    watchlist_entry=(await db.execute(query)).scalar_one_or_none()
    if watchlist_entry:
        await db.delete(watchlist_entry)
        await db.commit()
    return watchlist_entry

