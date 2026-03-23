import argparse

from app.db.session import SessionLocal
from app.services.ingestion.article_ingestion_service import ArticleIngestionService


def main() -> None:
    parser = argparse.ArgumentParser(description="Load article JSON into the database.")
    parser.add_argument("--file", required=True, help="Path to JSON file containing article array")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        service = ArticleIngestionService(db)
        count = service.load_file(args.file)
        print(f"Loaded {count} articles from {args.file}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
