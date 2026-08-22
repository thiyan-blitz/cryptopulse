import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import ForeignKey,Numeric,String,DateTime
from datetime import datetime
from app.database.base import Base
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.Coin import Coin

    
class PriceHistory(Base):
    __tablename__="price_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    coin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("coin.id", ondelete="CASCADE")
    )

    interval:Mapped[str]=mapped_column(String)
    open:Mapped[Decimal]=mapped_column(Numeric)
    close:Mapped[Decimal]=mapped_column(Numeric)
    high:Mapped[Decimal]=mapped_column(Numeric)
    low:Mapped[Decimal]=mapped_column(Numeric)
    volume:Mapped[Decimal]=mapped_column(Numeric,default=0.0)
    ts:Mapped[datetime]=mapped_column(DateTime(timezone=True),primary_key=True,index=True)

    coin:Mapped["Coin"] = relationship(back_populates="price_history")