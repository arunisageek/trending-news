from sqlalchemy import select

from app.db.models.article import Article
from app.schemas.event import EventCreate
from app.services.events.event_ingestion_service import EventIngestionService
from app.services.ranking.trending_score_service import TrendingScoreService


def test_trending_api_returns_articles(client, db_session) -> None:
    article = db_session.scalars(select(Article)).first()
    assert article is not None

    ingestion = EventIngestionService(db_session)
    ingestion.ingest_event(
        EventCreate(
            article_id=article.id,
            event_type="view",
            user_lat=28.6139,
            user_lon=77.2090,
            user_id="u-1",
        )
    )

    TrendingScoreService(db_session).recompute_scores()

    response = client.get("/api/v1/trending", params={"lat": 28.6139, "lon": 77.2090, "limit": 5})
    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["result_count"] >= 1
    assert len(payload["articles"]) >= 1
