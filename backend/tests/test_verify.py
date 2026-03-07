# tests/test_verify.py
"""Ce fichier permet de tester la fonctionnalité “vérification d’email” de bout en bout côté backend, en couvrant les cas principaux :

succès

token invalide

token expiré

utilisateur déjà vérifié

code correct

code incorrect

code expiré

renvoi d’email inutile"""
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock, Mock

from itsdangerous import SignatureExpired, BadSignature

import app.api.auth as auth_module
from app.services.user_service import UserService
from app.schemas.email_schemas import (
    ResendEmailVerificationCodeModel,
    EmailVerificationCodeVerifyModel,
    Email,
)

from tests.helpers import make_payload

AUTH = "/auth"


def test_verify_success(client, monkeypatch):
    token = "good-token"
    monkeypatch.setattr(auth_module, "decode_url_safe_token", Mock(return_value={"email": "u@example.com"}))

    fake_user = SimpleNamespace(email="u@example.com", id=uuid4(), is_verified=False)
    monkeypatch.setattr(UserService, "get_user_by_email", AsyncMock(return_value=fake_user))

    update_mock = AsyncMock()
    monkeypatch.setattr(UserService, "update_user", update_mock)

    resp = client.get(f"{AUTH}/verify/{token}", follow_redirects=False)
    assert resp.status_code in (302, 303, 307), resp.text
    assert resp.headers["location"] == "http://localhost:4200/login?verify=success"
    update_mock.assert_awaited_once()


def test_verify_invalid_token(client, monkeypatch):
    monkeypatch.setattr(auth_module, "decode_url_safe_token", Mock(side_effect=BadSignature("bad")))

    resp = client.get(f"{AUTH}/verify/bad-token", follow_redirects=False)
    assert resp.status_code == 400, resp.text


def test_verify_expired_token(client, monkeypatch):
    monkeypatch.setattr(auth_module, "decode_url_safe_token", Mock(side_effect=SignatureExpired("expired")))

    resp = client.get(f"{AUTH}/verify/expired-token", follow_redirects=False)
    assert resp.status_code in (302, 303, 307), resp.text
    assert resp.headers["location"] == "http://localhost:4200/login?verify=expired"


def test_verify_already_verified(client, monkeypatch):
    monkeypatch.setattr(auth_module, "decode_url_safe_token", Mock(return_value={"email": "u@example.com"}))

    fake_user = SimpleNamespace(email="u@example.com", id=uuid4(), is_verified=True)
    monkeypatch.setattr(UserService, "get_user_by_email", AsyncMock(return_value=fake_user))

    update_mock = AsyncMock()
    monkeypatch.setattr(UserService, "update_user", update_mock)

    resp = client.get(f"{AUTH}/verify/ok-token", follow_redirects=False)
    assert resp.status_code in (302, 303, 307), resp.text
    assert resp.headers["location"] == "http://localhost:4200/login?verify=already"
    update_mock.assert_not_awaited()


def test_send_verification_code_success(client, monkeypatch):
    payload = make_payload(ResendEmailVerificationCodeModel, overrides={"email": "u@example.com"})

    fake_user = SimpleNamespace(email=payload["email"], id=uuid4(), is_verified=False)
    monkeypatch.setattr(UserService, "get_user_by_email", AsyncMock(return_value=fake_user))

    monkeypatch.setattr(auth_module.random, "randint", Mock(return_value=123456))
    monkeypatch.setattr(auth_module, "hash", Mock(return_value="HASHED_CODE"))

    store_mock = AsyncMock()
    monkeypatch.setattr(auth_module, "store_email_verification_code", store_mock)

    send_mock = Mock()
    monkeypatch.setattr(auth_module, "send_verification_code_email", send_mock)

    resp = client.post(f"{AUTH}/send-verification-code", json=payload)
    assert resp.status_code == 200, resp.text
    store_mock.assert_awaited_once_with(payload["email"], "HASHED_CODE")
    send_mock.assert_called_once()


def test_verify_email_code_success(client, monkeypatch):
    payload = make_payload(EmailVerificationCodeVerifyModel, overrides={
        "email": "u@example.com",
        "code": "123456",
    })

    monkeypatch.setattr(auth_module, "get_email_verification_code", AsyncMock(return_value="HASHED_CODE"))
    monkeypatch.setattr(auth_module, "verify", Mock(return_value=True))

    fake_user = SimpleNamespace(email=payload["email"], id=uuid4(), is_verified=False)
    monkeypatch.setattr(UserService, "get_user_by_email", AsyncMock(return_value=fake_user))

    update_mock = AsyncMock()
    monkeypatch.setattr(UserService, "update_user", update_mock)

    delete_mock = AsyncMock()
    monkeypatch.setattr(auth_module, "delete_email_verification_code", delete_mock)

    resp = client.post(f"{AUTH}/verify-email-code", json=payload)
    assert resp.status_code == 200, resp.text
    update_mock.assert_awaited_once()
    delete_mock.assert_awaited_once_with(payload["email"])


def test_verify_email_code_invalid(client, monkeypatch):
    payload = make_payload(EmailVerificationCodeVerifyModel, overrides={"email": "u@example.com", "code": "999999"})
    monkeypatch.setattr(auth_module, "get_email_verification_code", AsyncMock(return_value="HASHED_CODE"))
    monkeypatch.setattr(auth_module, "verify", Mock(return_value=False))

    resp = client.post(f"{AUTH}/verify-email-code", json=payload)
    assert resp.status_code in (400, 401), resp.text


def test_verify_email_code_expired(client, monkeypatch):
    payload = make_payload(EmailVerificationCodeVerifyModel, overrides={"email": "u@example.com", "code": "123456"})
    monkeypatch.setattr(auth_module, "get_email_verification_code", AsyncMock(return_value=None))

    resp = client.post(f"{AUTH}/verify-email-code", json=payload)
    assert resp.status_code in (400, 401), resp.text


def test_resend_verification_email_user_already_verified(client, monkeypatch):
    payload = make_payload(Email, overrides={"email": "u@example.com"})

    fake_user = SimpleNamespace(email=payload["email"], id=uuid4(), is_verified=True)
    monkeypatch.setattr(UserService, "get_user_by_email", AsyncMock(return_value=fake_user))

    store_mock = AsyncMock()
    monkeypatch.setattr(auth_module, "store_email_verification_code", store_mock)

    send_mock = Mock()
    monkeypatch.setattr(auth_module, "send_verification_code_email", send_mock)

    resp = client.post(f"{AUTH}/resend-verification-email", json=payload)
    assert resp.status_code == 200, resp.text
    store_mock.assert_not_awaited()
    send_mock.assert_not_called()