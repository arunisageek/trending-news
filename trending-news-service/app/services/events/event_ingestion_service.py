from sqlalchemy.orm import Session

from app.api.errors import AppException
from app.core.constants import EVENT_WEIGHTS
from app.db.models.user_event import UserEvent
from app.db.repositories.article_repository import ArticleRepository
from app.db.repositories.event_repository import EventRepository
from app.schemas.event import EventCreate
from app.services.cache.cache_service import cache_service
from app.services.geo.bucket_service import BucketService


class EventIngestionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.article_repo = ArticleRepository(db)
        self.event_repo = EventRepository(db)
        self.bucket_service = BucketService()

    def ingest_event(self, payload: EventCreate) -> UserEvent:
        article = self.article_repo.get(payload.article_id)
        if article is None:
            raise AppException(status_code=404, code="ARTICLE_NOT_FOUND", message="Article does not exist")

        bucket_id = self.bucket_service.bucket_id(payload.user_lat, payload.user_lon)
        event = UserEvent(
            event_id=payload.event_id,
            user_id=payload.user_id,
            session_id=payload.session_id,
            article_id=payload.article_id,
            event_type=payload.event_type,
            event_ts=payload.event_ts,
            user_lat=payload.user_lat,
            user_lon=payload.user_lon,
            bucket_id=bucket_id,
            event_weight=EVENT_WEIGHTS[payload.event_type],
        )
        created = self.event_repo.create(event)
        cache_service.invalidate_bucket(bucket_id)
        return created
