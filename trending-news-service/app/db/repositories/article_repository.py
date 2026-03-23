from datetime import datetime
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.article import Article


class ArticleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert_many(self, articles: Iterable[dict]) -> int:
        count = 0
        for payload in articles:
            article = self.db.get(Article, payload["id"])
            if article is None:
                article = Article(**payload)
                self.db.add(article)
            else:
                article.title = payload["title"]
                article.description = payload.get("description")
                article.url = payload["url"]
                article.publication_date = payload["publication_date"]
                article.source_name = payload["source_name"]
                article.category = payload["category"]
                article.relevance_score = payload["relevance_score"]
                article.latitude = payload["latitude"]
                article.longitude = payload["longitude"]
                article.llm_summary = payload.get("llm_summary")
            count += 1
        self.db.commit()
        return count

    def get(self, article_id: str) -> Article | None:
        return self.db.get(Article, article_id)

    def list_all(self) -> list[Article]:
        stmt = select(Article).order_by(Article.publication_date.desc())
        return list(self.db.scalars(stmt).all())

    def count(self) -> int:
        return len(self.list_all())

    def random_candidates(self, limit: int = 100) -> list[Article]:
        articles = self.list_all()
        return articles[:limit]

    def latest_publication(self) -> datetime | None:
        stmt = select(Article).order_by(Article.publication_date.desc()).limit(1)
        return self.db.scalar(stmt)
