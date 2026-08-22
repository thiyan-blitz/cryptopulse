from sqlalchemy.orm import Mapped,mapped_column,relationship
import uuid
from datetime import datetime
from app.database.base import Base
from sqlalchemy import ForeignKey,Numeric,DateTime,func
from decimal import Decimal
from sqlalchemy.dialects.postgresql import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.Coin import Coin
    from app.models.User import User
    
class Holding(Base):
    __tablename__="holding"

    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("user.id"))

    coin_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("coin.id"))

    quantity:Mapped[Decimal]=mapped_column(Numeric(20,8),default=0.0)
    avg_buy_price:Mapped[Decimal]=mapped_column(Numeric(20,8),default=0.0)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="holdings")
    coin: Mapped["Coin"] = relationship()

