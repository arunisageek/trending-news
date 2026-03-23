from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserEvent(Base):
    __tablename__ = "user_events"

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    session_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    article_id: Mapped[str] = mapped_column(String(36), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    event_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    user_lat: Mapped[float] = mapped_column(Float, nullable=False)
    user_lon: Mapped[float] = mapped_column(Float, nullable=False)
    bucket_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_weight: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    article = relationship("Article")

    __table_args__ = (
        Index("ix_user_events_bucket_time", "bucket_id", "event_ts"),
        Index("ix_user_events_article_time", "article_id", "event_ts"),
    )
