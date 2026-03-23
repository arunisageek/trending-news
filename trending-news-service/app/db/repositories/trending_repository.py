from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models.trending_score import TrendingScore


class TrendingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert_many(self, records: list[TrendingScore]) -> None:
        for record in records:
            existing = self.db.get(
                TrendingScore,
                {
                    "bucket_id": record.bucket_id,
                    "article_id": record.article_id,
                    "score_window": record.score_window,
                },
            )
            if existing is None:
                self.db.add(record)
                continue

            existing.trend_score = record.trend_score
            existing.views_count = record.views_count
            existing.clicks_count = record.clicks_count
            existing.shares_count = record.shares_count
            existing.bookmarks_count = record.bookmarks_count
            existing.last_event_ts = record.last_event_ts
            existing.computed_at = record.computed_at

        self.db.commit()

    def delete_bucket_scores(self, bucket_ids: list[str], score_window: str) -> None:
        self.db.execute(
            delete(TrendingScore).where(
                TrendingScore.bucket_id.in_(bucket_ids),
                TrendingScore.score_window == score_window,
            )
        )
        self.db.commit()

    def fetch_bucket_scores(self, bucket_ids: list[str], score_window: str) -> list[TrendingScore]:
        stmt = (
            select(TrendingScore)
            .where(TrendingScore.bucket_id.in_(bucket_ids), TrendingScore.score_window == score_window)
            .order_by(TrendingScore.trend_score.desc())
        )
        return list(self.db.scalars(stmt).all())

    def latest_computation_for_buckets(self, bucket_ids: list[str], score_window: str) -> datetime | None:
        stmt = (
            select(TrendingScore.computed_at)
            .where(TrendingScore.bucket_id.in_(bucket_ids), TrendingScore.score_window == score_window)
            .order_by(TrendingScore.computed_at.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)
