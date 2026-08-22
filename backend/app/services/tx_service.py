import uuid
from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy import select, asc, desc
from sqlalchemy.orm import selectinload  
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.Transaction import Transaction
from app.schemas.transaction import TransactionFilter

async def get_transactions_with_filters(
    db: AsyncSession, user_id: uuid.UUID, filters: TransactionFilter):

    query = (
        select(Transaction)
        .options(selectinload(Transaction.coin))
        .where(Transaction.user_id == user_id)
    )

    if filters.coin_id:
        query = query.where(Transaction.coin_id == filters.coin_id)

    if filters.tx_type:
        query = query.where(Transaction.tx_type == filters.tx_type)

    if filters.time_range:
        now = datetime.now(timezone.utc)
        if filters.time_range == "last_hour":
            time_threshold = now - timedelta(hours=1)
        elif filters.time_range == "last_day":
            time_threshold = now - timedelta(days=1)
        elif filters.time_range == "last_week":
            time_threshold = now - timedelta(weeks=1)
        elif filters.time_range == "last_month":
            time_threshold = now - timedelta(days=30)
        else:
            time_threshold = None

        if time_threshold:
            query = query.where(Transaction.created_at >= time_threshold)

    sort_column_map = {
        "price_at_trade": Transaction.price_at_trade,
        "quantity": Transaction.quantity,
        "created_at": Transaction.created_at,
        "total_value": Transaction.total_value,
    }
    sort_column = sort_column_map.get(filters.sort_by, Transaction.created_at)

    if filters.sort_order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    result = await db.execute(query)
    db_transactions = result.scalars().all()

    return [
        {
            "id": tx.id,
            "user_id": tx.user_id,
            "coin_id": tx.coin_id,
            "symbol": tx.coin.symbol if tx.coin else "N/A",  # 👈 Directly access tx.coin.symbol
            "tx_type": tx.tx_type,
            "quantity": tx.quantity,
            "price_at_trade": tx.price_at_trade,
            "total_value": tx.total_value,
            "created_at": tx.created_at,
        }
        for tx in db_transactions
    ]