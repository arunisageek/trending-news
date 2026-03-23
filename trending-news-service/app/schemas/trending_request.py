from pydantic import BaseModel, Field


class TrendingRequest(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    limit: int = Field(default=5, ge=1, le=100)
    radius_km: float | None = Field(default=None, gt=0)
