from app.db.session import SessionLocal
from app.services.ranking.trending_score_service import TrendingScoreService


def main() -> None:
    db = SessionLocal()
    try:
        service = TrendingScoreService(db)
        count = service.recompute_scores()
        print(f"Recomputed {count} trending score rows")
    finally:
        db.close()


if __name__ == "__main__":
    main()
