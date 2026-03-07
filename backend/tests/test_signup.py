# tests/test_signup.py
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock, Mock

import app.api.auth as auth_module
from app.services.user_service import UserService
from app.schemas.user_schemas import UserCreate

from tests.helpers import make_payload

AUTH = "/auth"


def test_signup_success(client, monkeypatch):
    payload = make_payload(UserCreate, overrides={"email": "new.user@example.com"})

    monkeypatch.setattr(UserService, "user_exists", AsyncMock(return_value=False))

    fake_user = SimpleNamespace(
        email=payload["email"],
        id=uuid4(),
        is_verified=False,
        hashed_password="HASHED",
        roles=[],
    )
    monkeypatch.setattr(UserService, "create_user", AsyncMock(return_value=fake_user))

    monkeypatch.setattr(auth_module.random, "randint", Mock(return_value=123456))
    monkeypatch.setattr(auth_module, "hash", Mock(return_value="HASHED_CODE"))

    store_mock = AsyncMock()
    monkeypatch.setattr(auth_module, "store_email_verification_code", store_mock)

    send_mock = Mock()
    monkeypatch.setattr(auth_module, "send_verification_code_email", send_mock)

    resp = client.post(f"{AUTH}/signup", json=payload)
    assert resp.status_code == 201, resp.text

    data = resp.json()
    assert data["email"] == payload["email"]
    store_mock.assert_awaited_once_with(payload["email"], "HASHED_CODE")
    send_mock.assert_called_once()
    assert send_mock.call_args.args[1] == "123456"


def test_signup_existing_email(client, monkeypatch):
    payload = make_payload(UserCreate, overrides={"email": "exists@example.com"})
    monkeypatch.setattr(UserService, "user_exists", AsyncMock(return_value=True))

    resp = client.post(f"{AUTH}/signup", json=payload)
    assert resp.status_code ==403, resp.text


def test_signup_invalid_email(client):
    payload = make_payload(UserCreate, overrides={"email": "not-an-email"})
    resp = client.post(f"{AUTH}/signup", json=payload)
    assert resp.status_code == 422, resp.text


def test_signup_weak_password(client):
    payload = make_payload(UserCreate, overrides={"password": "123"})
    resp = client.post(f"{AUTH}/signup", json=payload)
    assert resp.status_code in (422, 400), resp.text


def test_signup_missing_fields(client):
    payload = make_payload(UserCreate)
    payload.pop("email", None)

    resp = client.post(f"{AUTH}/signup", json=payload)
    assert resp.status_code == 422, resp.text