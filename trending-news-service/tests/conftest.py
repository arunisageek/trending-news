from collections.abc import Generator
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import get_db
from app.db.base import Base
from app.db.models.article import Article
from app.main import app


@pytest.fixture()
def db_session(tmp_path: Path) -> Generator[Session, None, None]:
    db_file = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        now = datetime.now(timezone.utc)
        session.add_all(
            [
                Article(
                    id=str(uuid4()),
                    title="Delhi local article",
                    description="Local traffic update",
                    url="https://example.com/1",
                    publication_date=now - timedelta(hours=2),
                    source_name="Example",
                    category=["General"],
                    relevance_score=0.5,
                    latitude=28.6139,
                    longitude=77.2090,
                    llm_summary="Summary 1",
                ),
                Article(
                    id=str(uuid4()),
                    title="Noida startup article",
                    description="Funding update",
                    url="https://example.com/2",
                    publication_date=now - timedelta(hours=1),
                    source_name="Example",
                    category=["Business"],
                    relevance_score=0.9,
                    latitude=28.5355,
                    longitude=77.3910,
                    llm_summary="Summary 2",
                ),
            ]
        )
        session.commit()
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
