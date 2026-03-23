from datetime import datetime

from sqlalchemy import delete, distinct, select
from sqlalchemy.orm import Session

from app.db.models.user_event import UserEvent


class EventRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, event: UserEvent) -> UserEvent:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def recent_events(self, since: datetime, bucket_ids: list[str] | None = None) -> list[UserEvent]:
        stmt = select(UserEvent).where(UserEvent.event_ts >= since)
        if bucket_ids:
            stmt = stmt.where(UserEvent.bucket_id.in_(bucket_ids))
        stmt = stmt.order_by(UserEvent.event_ts.desc())
        return list(self.db.scalars(stmt).all())

    def active_bucket_ids(self, since: datetime) -> list[str]:
        stmt = select(distinct(UserEvent.bucket_id)).where(UserEvent.event_ts >= since)
        return list(self.db.scalars(stmt).all())

    def clear(self) -> None:
        self.db.execute(delete(UserEvent))
        self.db.commit()
