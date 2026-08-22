import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.database.base import Base
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.Coin import Coin
    from app.models.User import User
    
class WatchList(Base):
    __tablename__="watchlist"

    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("user.id"))

    coin_id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),ForeignKey("coin.id"))

    user: Mapped["User"] = relationship(back_populates="watchlist")
    coin: Mapped["Coin"] = relationship()