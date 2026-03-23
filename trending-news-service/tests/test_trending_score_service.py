from app.schemas.event import EventCreate
from app.services.events.event_ingestion_service import EventIngestionService
from app.services.ranking.trending_score_service import TrendingScoreService


def test_recompute_scores_creates_rank_rows(db_session) -> None:
    article = db_session.query(type(db_session.query)).first
    first_article = db_session.execute(__import__("sqlalchemy").select(__import__("app.db.models.article", fromlist=["Article"]).Article)).scalars().first()

    ingestion = EventIngestionService(db_session)
    ingestion.ingest_event(
        EventCreate(
            article_id=first_article.id,
            event_type="click",
            user_lat=28.6139,
            user_lon=77.2090,
            user_id="user-1",
        )
    )

    service = TrendingScoreService(db_session)
    count = service.recompute_scores()
    assert count >= 1
