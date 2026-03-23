import math
import random
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.constants import EVENT_WEIGHTS
from app.db.models.user_event import UserEvent
from app.db.repositories.article_repository import ArticleRepository
from app.db.repositories.event_repository import EventRepository
from app.schemas.event import EventSimulationResponse
from app.services.cache.cache_service import cache_service
from app.services.geo.bucket_service import BucketService


class EventSimulatorService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.article_repo = ArticleRepository(db)
        self.event_repo = EventRepository(db)
        self.bucket_service = BucketService()

    def simulate(self, count: int = 100) -> EventSimulationResponse:
        articles = self.article_repo.list_all()
        if not articles:
            raise ValueError("No articles available to simulate events")

        created = 0
        touched: set[str] = set()
        now = datetime.now(timezone.utc)

        for _ in range(count):
            article = random.choice(articles)
            event_type = random.choices(
                population=["view", "click", "share", "bookmark"],
                weights=[70, 20, 5, 5],
                k=1,
            )[0]

            lat, lon = self._random_point_near(article.latitude, article.longitude, radius_km=15.0)
            bucket_id = self.bucket_service.bucket_id(lat, lon)
            event = UserEvent(
                event_id=str(uuid4()),
                user_id=f"user-{random.randint(1, 5000)}",
                session_id=str(uuid4()),
                article_id=article.id,
                event_type=event_type,
                event_ts=now - timedelta(minutes=random.randint(0, 1440)),
                user_lat=lat,
                user_lon=lon,
                bucket_id=bucket_id,
                event_weight=EVENT_WEIGHTS[event_type],
            )
            self.db.add(event)
            touched.add(bucket_id)
            created += 1

        self.db.commit()
        for bucket in touched:
            cache_service.invalidate_bucket(bucket)

        return EventSimulationResponse(created_count=created, buckets_touched=sorted(touched))

    def _random_point_near(self, lat: float, lon: float, radius_km: float) -> tuple[float, float]:
        radius_in_degrees = radius_km / 111.0
        u = random.random()
        v = random.random()
        w = radius_in_degrees * math.sqrt(u)
        t = 2 * math.pi * v
        dlat = w * math.cos(t)
        dlon = w * math.sin(t) / max(math.cos(math.radians(lat)), 0.01)
        return lat + dlat, lon + dlon
