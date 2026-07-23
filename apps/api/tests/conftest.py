from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite+pysqlite://"
os.environ["AUTH_USERNAME"] = "mezie"
os.environ["AUTH_PASSWORD"] = "brandos-local-dev"
os.environ["SESSION_SECRET"] = "test-session-secret-with-enough-entropy"

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.seed import seed_database


@pytest.fixture
def db() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with testing_session() as session:
        source_root = Path(__file__).resolve().parents[3] / "docs" / "source"
        seed_database(session, source_root)
        yield session
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_client(client: TestClient) -> TestClient:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "mezie", "password": "brandos-local-dev"},
    )
    assert response.status_code == 200
    return client
