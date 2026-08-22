from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.database.base import Base
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.Holding import Holding
    from app.models.PriceHistory import PriceHistory
    

class Coin(Base):
    __tablename__="coin"

    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    symbol:Mapped[str]=mapped_column(String,unique=True,index=True)
    name:Mapped[str]=mapped_column(String,unique=True,index=True)
    logo_url:Mapped[str]=mapped_column(String)

    holdings: Mapped[list["Holding"]] = relationship(back_populates="coin")
    price_history: Mapped[list["PriceHistory"]] = relationship()