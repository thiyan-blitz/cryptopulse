from sqlalchemy import String,DateTime,func
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.database.base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.Holding import Holding
    from app.models.Wallet import Wallet
    from app.models.Transaction import Transaction
    from app.models.WatchList import WatchList
class User(Base):
    __tablename__="user"
    id:Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email:Mapped[str]=mapped_column(String,unique=True)
    password:Mapped[str]=mapped_column(String)
    username:Mapped[str]=mapped_column(String,unique=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())

    wallet: Mapped["Wallet"] = relationship(back_populates="user", uselist=False)
    holdings: Mapped[list["Holding"]] = relationship(back_populates="user")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user")
    watchlist: Mapped[list["WatchList"]] = relationship(back_populates="user")