from sqlalchemy.orm import mapped_column,Mapped,relationship
from app.database.base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey

class news_coin_tags(Base):
    __tablename__="news_coin_tag"

    news_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("news_articles.id"),primary_key=True
    )
    coin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("coin.id", ondelete="CASCADE"),primary_key=True
    )