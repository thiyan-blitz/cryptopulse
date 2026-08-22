import uuid
from sqlalchemy.orm import mapped_column,Mapped,relationship
from app.database.base import Base
from sqlalchemy import ForeignKey,String,Numeric,DateTime,func
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.Coin import Coin
    from app.models.User import User

class Transaction(Base):
    __tablename__="transaction"

    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("user.id"))

    coin_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("coin.id"))

    tx_type:Mapped[str]=mapped_column(String)
    quantity:Mapped[Decimal]=mapped_column(Numeric)
    price_at_trade:Mapped[Decimal]=mapped_column(Numeric)
    total_value:Mapped[Decimal]=mapped_column(Numeric)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="transactions")
    coin: Mapped["Coin"] = relationship()