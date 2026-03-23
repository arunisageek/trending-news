from datetime import datetime

from pydantic import BaseModel, Field


class ArticleBase(BaseModel):
    id: str
    title: str
    description: str | None = None
    url: str
    publication_date: datetime
    source_name: str
    category: list[str]
    relevance_score: float = Field(ge=0)
    latitude: float
    longitude: float
    llm_summary: str | None = None


class ArticleOut(ArticleBase):
    trend_score: float | None = None
    distance_km: float | None = None
    engagement: dict | None = None

    model_config = {"from_attributes": True}
