from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TrendingScore(Base):
    __tablename__ = "trending_scores"

    bucket_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    article_id: Mapped[str] = mapped_column(String(36), ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True)
    score_window: Mapped[str] = mapped_column(String(20), primary_key=True, default="24h")
    trend_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    views_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    clicks_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    shares_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bookmarks_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_event_ts: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    article = relationship("Article")

    __table_args__ = (
        Index("ix_trending_scores_lookup", "bucket_id", "score_window", "trend_score"),
    )
