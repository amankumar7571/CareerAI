"""Pytest setup for the CareerAI backend.

Sets test-only environment variables BEFORE the app is imported, so the
settings singleton and the SQLAlchemy engine point at throwaway locations
instead of the developer's real database and upload folder.
"""
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

TEST_DB = Path("/tmp/careerai_test.db")
TEST_UPLOADS = Path("/tmp/careerai_test_uploads")

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["UPLOAD_DIR"] = str(TEST_UPLOADS)
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
# GEMINI_API_KEY is deliberately NOT set: skill extraction then falls back
# to the local spaCy / keyword path, so tests run without network or keys.

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models
from auth import get_current_user
from database import get_db
from main import app

TEST_ENGINE = create_engine(
    f"sqlite:///{TEST_DB}", connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)
models.Base.metadata.create_all(bind=TEST_ENGINE)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


class _FakeUser:
    """Stand-in for the authenticated user; the real dependency needs a JWT."""

    user_id = 1
    name = "Test User"
    email = "test@example.com"
    cgpa = 8.0


@pytest.fixture()
def client():
    """TestClient with auth and DB dependencies overridden (no real login)."""
    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = lambda: _FakeUser()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def bare_client():
    """TestClient with NO overrides, for testing auth rejection."""
    app.dependency_overrides.clear()
    with TestClient(app) as c:
        yield c
