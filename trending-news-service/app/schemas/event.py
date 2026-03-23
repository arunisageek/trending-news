from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from app.core.constants import VALID_EVENT_TYPES


class EventCreate(BaseModel):
    article_id: str
    event_type: str
    user_lat: float = Field(ge=-90, le=90)
    user_lon: float = Field(ge=-180, le=180)
    user_id: str | None = None
    session_id: str | None = None
    event_ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str = Field(default_factory=lambda: str(uuid4()))

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, value: str) -> str:
        if value not in VALID_EVENT_TYPES:
            raise ValueError(f"event_type must be one of {sorted(VALID_EVENT_TYPES)}")
        return value


class EventCreateResponse(BaseModel):
    event_id: str
    article_id: str
    event_type: str
    user_lat: float
    user_lon: float
    user_id: str | None = None
    session_id: str | None = None
    event_ts: datetime
    bucket_id: str

    model_config = {"from_attributes": True}


class EventSimulationResponse(BaseModel):
    created_count: int
    buckets_touched: list[str]
