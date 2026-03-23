import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.repositories.article_repository import ArticleRepository


class ArticleIngestionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ArticleRepository(db)

    def load_file(self, file_path: str | Path) -> int:
        path = Path(file_path)
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)

        if not isinstance(raw, list):
            raise ValueError("Article file must contain a JSON array")

        normalized = [self._normalize_article(item) for item in raw]
        return self.repo.upsert_many(normalized)

    def _normalize_article(self, payload: dict) -> dict:
        publication = payload["publication_date"]
        if publication.endswith("Z"):
            publication_dt = datetime.fromisoformat(publication.replace("Z", "+00:00"))
        else:
            publication_dt = datetime.fromisoformat(publication)
            if publication_dt.tzinfo is None:
                publication_dt = publication_dt.replace(tzinfo=timezone.utc)

        return {
            "id": payload["id"],
            "title": payload["title"].strip(),
            "description": (payload.get("description") or "").strip(),
            "url": payload["url"].strip(),
            "publication_date": publication_dt,
            "source_name": payload["source_name"].strip(),
            "category": payload.get("category") or [],
            "relevance_score": float(payload["relevance_score"]),
            "latitude": float(payload["latitude"]),
            "longitude": float(payload["longitude"]),
            "llm_summary": payload.get("llm_summary"),
        }
