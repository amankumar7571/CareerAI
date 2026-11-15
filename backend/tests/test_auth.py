"""Tests for the JWT auth flow: register, login, and /me.

These exercise the REAL auth dependency (no get_current_user override),
against the throwaway test database from conftest.py. Run from backend/:
    python -m pytest tests/test_auth.py -v
"""
import uuid

import pytest
from fastapi.testclient import TestClient

from conftest import _override_get_db
from auth import get_current_user
from database import get_db
from main import app


@pytest.fixture()
def auth_client():
    """TestClient with the test DB wired in but the real JWT auth live."""
    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = _override_get_db
    # Deliberately NO override for get_current_user: these tests prove
    # the real bcrypt + JWT flow works end to end.
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _unique_email():
    return f"user-{uuid.uuid4().hex[:12]}@example.com"


def _register(client, email, password="correct-horse-battery"):
    return client.post(
        "/api/auth/register",
        json={"name": "Auth Test", "email": email, "password": password},
    )


def _login(client, email, password="correct-horse-battery"):
    return client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
    )


def test_register_success_returns_201_without_password(auth_client):
    email = _unique_email()
    resp = _register(auth_client, email)
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == email
    assert body["name"] == "Auth Test"
    assert "user_id" in body
    assert "password" not in body


def test_register_duplicate_email_returns_400(auth_client):
    email = _unique_email()
    assert _register(auth_client, email).status_code == 201
    resp = _register(auth_client, email)
    assert resp.status_code == 400


def test_login_success_returns_bearer_token(auth_client):
    email = _unique_email()
    assert _register(auth_client, email).status_code == 201
    resp = _login(auth_client, email)
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert len(body["access_token"].split(".")) == 3  # header.payload.signature


def test_login_wrong_password_returns_401(auth_client):
    email = _unique_email()
    assert _register(auth_client, email).status_code == 201
    resp = _login(auth_client, email, password="definitely-wrong")
    assert resp.status_code == 401


def test_login_unknown_email_returns_401(auth_client):
    resp = _login(auth_client, _unique_email())
    assert resp.status_code == 401


def test_me_without_token_returns_401(auth_client):
    resp = auth_client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_with_token_returns_current_user(auth_client):
    email = _unique_email()
    assert _register(auth_client, email).status_code == 201
    token = _login(auth_client, email).json()["access_token"]
    resp = auth_client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == email


def test_me_with_bad_token_returns_401(auth_client):
    resp = auth_client.get(
        "/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert resp.status_code == 401
