# tests/test_login.py
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock, Mock

import app.api.auth as auth_module
from app.services.user_service import UserService
from app.schemas.user_schemas import UserLogin

from tests.helpers import make_payload

AUTH = "/auth"


def test_login_success(client, monkeypatch):
    payload = make_payload(UserLogin, overrides={"email": "user@example.com"})

    fake_user = SimpleNamespace(
        email=payload["email"],
        hashed_password="HASHED_PW",
        is_verified=True,
        id=uuid4(),
        roles=[SimpleNamespace(name="admin")],
    )

    monkeypatch.setattr(UserService, "get_user_by_email", AsyncMock(return_value=fake_user))
    monkeypatch.setattr(auth_module, "verify", Mock(return_value=True))

    def fake_create_access_token(*, user_data, refresh=False, expiry=None):
        return "REFRESH_TOKEN" if refresh else "ACCESS_TOKEN"

    monkeypatch.setattr(auth_module, "create_access_token", fake_create_access_token)

    resp = client.post(f"{AUTH}/login", json=payload)
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert data["access_token"] == "ACCESS_TOKEN"
    assert resp.cookies.get("refresh_token") == "REFRESH_TOKEN"
    assert data["user"]["roles"] == ["admin"]

    set_cookie = (resp.headers.get("set-cookie") or "").lower()
    assert "httponly" in set_cookie


def test_login_wrong_password(client, monkeypatch):
    payload = make_payload(UserLogin, overrides={"email": "user@example.com"})

    fake_user = SimpleNamespace(
        email=payload["email"],
        hashed_password="HASHED_PW",
        is_verified=True,
        id=uuid4(),
        roles=[],
    )
    monkeypatch.setattr(UserService, "get_user_by_email", AsyncMock(return_value=fake_user))
    monkeypatch.setattr(auth_module, "verify", Mock(return_value=False))

    resp = client.post(f"{AUTH}/login", json=payload)
   # assert resp.status_code in (401, 403), resp.text
    assert resp.status_code == 400, resp.text


def test_login_nonexistent_user(client, monkeypatch):
    payload = make_payload(UserLogin, overrides={"email": "missing@example.com"})
    monkeypatch.setattr(UserService, "get_user_by_email", AsyncMock(return_value=None))

    resp = client.post(f"{AUTH}/login", json=payload)
    #assert resp.status_code in (401, 404), resp.text
    assert resp.status_code == 400, resp.text

def test_login_unverified_account(client, monkeypatch):
    payload = make_payload(UserLogin, overrides={"email": "notverified@example.com"})

    fake_user = SimpleNamespace(
        email=payload["email"],
        hashed_password="HASHED_PW",
        is_verified=False,
        id=uuid4(),
        roles=[],
    )
    monkeypatch.setattr(UserService, "get_user_by_email", AsyncMock(return_value=fake_user))
    monkeypatch.setattr(auth_module, "verify", Mock(return_value=True))

    resp = client.post(f"{AUTH}/login", json=payload)
    assert resp.status_code == 403, resp.text

def test_login_missing_fields(client):
    payload = make_payload(UserLogin)
    payload.pop("password", None)

    resp = client.post(f"{AUTH}/login", json=payload)
    assert resp.status_code == 422, resp.text