from datetime import datetime

from pydantic import BaseModel

from app.schemas.article import ArticleOut


class TrendingMeta(BaseModel):
    lat: float
    lon: float
    radius_km: float
    limit: int
    bucket_id: str
    generated_at: datetime
    cache_hit: bool
    result_count: int


class TrendingResponse(BaseModel):
    meta: TrendingMeta
    articles: list[ArticleOut]
