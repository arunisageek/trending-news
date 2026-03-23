from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.trending_response import TrendingResponse
from app.services.ranking.trending_score_service import TrendingScoreService

router = APIRouter(tags=["trending"])


@router.get("/trending", response_model=TrendingResponse)
def get_trending(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    limit: int = Query(default=5, ge=1, le=100),
    radius_km: float | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
) -> TrendingResponse:
    service = TrendingScoreService(db)
    return service.get_trending_feed(
        lat=lat,
        lon=lon,
        limit=limit,
        radius_km=radius_km,
    )
