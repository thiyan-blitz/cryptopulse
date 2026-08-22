from decimal import Decimal
import uuid
from app.models.Wallet import Wallet
from sqlalchemy.ext.asyncio import AsyncSession

async def create_wallet(db:AsyncSession,user_id:uuid.UUID):
    new_wallet = Wallet(user_id=user_id, balance_usd=Decimal("1000000.00"))
    db.add(new_wallet)

    return new_wallet

