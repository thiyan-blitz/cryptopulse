import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column,Mapped,relationship
from app.database.base import Base
from sqlalchemy import String,DateTime,Text
from typing import Optional
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.news_coin_tags import news_coin_tags
    
class NewsArticle(Base):
    __tablename__="news_articles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title:Mapped[str]=mapped_column(Text)
    source:Mapped[str]=mapped_column(String)
    url:Mapped[str]=mapped_column(String)
    sentiment:Mapped[Optional[str]]=mapped_column(String)
    published_at:Mapped[datetime]=mapped_column(DateTime(timezone=True))

    coin_tags: Mapped[list["news_coin_tags"]] = relationship()
