from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from math import exp

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models.trending_score import TrendingScore
from app.db.repositories.article_repository import ArticleRepository
from app.db.repositories.event_repository import EventRepository
from app.db.repositories.trending_repository import TrendingRepository
from app.schemas.article import ArticleOut
from app.schemas.trending_response import TrendingMeta, TrendingResponse
from app.services.cache.cache_service import cache_service
from app.services.geo.bucket_service import BucketService
from app.services.geo.distance_service import DistanceService
from app.utils.datetime_utils import utc_now
from app.utils.geohash_utils import neighboring_bucket_ids_map


class TrendingScoreService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.article_repo = ArticleRepository(db)
        self.event_repo = EventRepository(db)
        self.trending_repo = TrendingRepository(db)
        self.bucket_service = BucketService()
        self.distance_service = DistanceService()

    def get_trending_feed(self, lat: float, lon: float, limit: int, radius_km: float | None) -> TrendingResponse:
        limit = min(limit, self.settings.max_trending_limit)
        radius_km = radius_km or self.settings.default_radius_km
        primary_bucket = self.bucket_service.bucket(lat, lon)
        neighbor_map = neighboring_bucket_ids_map(primary_bucket)
        bucket_ids = list(neighbor_map.keys())

        cache_key = cache_service.feed_cache_key(primary_bucket.bucket_id, limit, radius_km)
        cached = cache_service.get(cache_key)
        if cached:
            cached_response = TrendingResponse.model_validate(cached)
            cached_response.meta.cache_hit = True
            return cached_response

        self._recompute_if_stale(bucket_ids)

        scores = self.trending_repo.fetch_bucket_scores(bucket_ids, self.settings.trending_score_window)
        articles_by_id = {}
        merged: dict[str, dict] = {}

        for score in scores:
            article = articles_by_id.get(score.article_id)
            if article is None:
                article = self.article_repo.get(score.article_id)
                if article is None:
                    continue
                articles_by_id[score.article_id] = article

            distance_km = self.distance_service.distance_km(lat, lon, article.latitude, article.longitude)
            if distance_km > radius_km:
                continue

            geo_weight = neighbor_map.get(score.bucket_id, self.settings.trending_neighbor_weight)
            weighted_score = score.trend_score * geo_weight

            if score.article_id not in merged:
                merged[score.article_id] = {
                    "article": article,
                    "weighted_score": 0.0,
                    "distance_km": distance_km,
                    "views": 0,
                    "clicks": 0,
                    "shares": 0,
                    "bookmarks": 0,
                }

            merged_item = merged[score.article_id]
            merged_item["weighted_score"] += weighted_score
            merged_item["views"] += score.views_count
            merged_item["clicks"] += score.clicks_count
            merged_item["shares"] += score.shares_count
            merged_item["bookmarks"] += score.bookmarks_count
            merged_item["distance_km"] = min(merged_item["distance_km"], distance_km)

        ranked = sorted(
            merged.values(),
            key=lambda item: (-item["weighted_score"], item["distance_km"], item["article"].publication_date),
        )[:limit]

        articles = [
            ArticleOut(
                id=item["article"].id,
                title=item["article"].title,
                description=item["article"].description,
                url=item["article"].url,
                publication_date=item["article"].publication_date,
                source_name=item["article"].source_name,
                category=item["article"].category,
                relevance_score=item["article"].relevance_score,
                latitude=item["article"].latitude,
                longitude=item["article"].longitude,
                llm_summary=item["article"].llm_summary,
                trend_score=round(item["weighted_score"], 4),
                distance_km=round(item["distance_km"], 3),
                engagement={
                    "views": item["views"],
                    "clicks": item["clicks"],
                    "shares": item["shares"],
                    "bookmarks": item["bookmarks"],
                },
            )
            for item in ranked
        ]

        response = TrendingResponse(
            meta=TrendingMeta(
                lat=lat,
                lon=lon,
                radius_km=radius_km,
                limit=limit,
                bucket_id=primary_bucket.bucket_id,
                generated_at=utc_now(),
                cache_hit=False,
                result_count=len(articles),
            ),
            articles=articles,
        )

        cache_service.set(cache_key, response.model_dump(mode="json"), self.settings.cache_ttl_seconds)
        return response

    def recompute_scores(self, bucket_ids: list[str] | None = None) -> int:
        lookback_since = utc_now() - timedelta(hours=self.settings.trending_lookback_hours)
        bucket_ids = bucket_ids or self.event_repo.active_bucket_ids(lookback_since)
        if not bucket_ids:
            return 0

        events = self.event_repo.recent_events(lookback_since, bucket_ids=bucket_ids)
        grouped: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
        for event in events:
            grouped[event.bucket_id][event.article_id].append(event)

        records: list[TrendingScore] = []
        now = utc_now()

        for bucket_id, article_map in grouped.items():
            for article_id, bucket_events in article_map.items():
                article = self.article_repo.get(article_id)
                if article is None:
                    continue

                counts = {"view": 0, "click": 0, "share": 0, "bookmark": 0}
                total_score = 0.0
                last_event_ts = None

                for event in bucket_events:
                    counts[event.event_type] += 1
                    age_hours = max((now - event.event_ts).total_seconds() / 3600, 0.0)
                    recency_factor = exp(-age_hours / self.settings.trending_decay_hours)
                    total_score += event.event_weight * recency_factor
                    if last_event_ts is None or event.event_ts > last_event_ts:
                        last_event_ts = event.event_ts

                article_age_hours = max((now - article.publication_date).total_seconds() / 3600, 0.0)
                freshness_boost = exp(-article_age_hours / 24)
                final_score = total_score + (0.25 * article.relevance_score) + (0.15 * freshness_boost)

                record = TrendingScore(
                    bucket_id=bucket_id,
                    article_id=article_id,
                    score_window=self.settings.trending_score_window,
                    trend_score=round(final_score, 6),
                    views_count=counts["view"],
                    clicks_count=counts["click"],
                    shares_count=counts["share"],
                    bookmarks_count=counts["bookmark"],
                    last_event_ts=last_event_ts,
                    computed_at=now,
                )
                records.append(record)

        self.trending_repo.delete_bucket_scores(bucket_ids, self.settings.trending_score_window)
        self.trending_repo.upsert_many(records)

        for bucket_id in bucket_ids:
            cache_service.invalidate_bucket(bucket_id)
        return len(records)

    def _recompute_if_stale(self, bucket_ids: list[str]) -> None:
        latest = self.trending_repo.latest_computation_for_buckets(bucket_ids, self.settings.trending_score_window)
        now = utc_now()
        if latest is None:
            self.recompute_scores(bucket_ids)
            return

        stale_after = timedelta(minutes=max(self.settings.cache_ttl_seconds // 60, 1))
        if now - latest > stale_after:
            self.recompute_scores(bucket_ids)
