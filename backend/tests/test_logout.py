# tests/test_logout.py
from unittest.mock import AsyncMock
from fastapi import HTTPException
from starlette.requests import Request

#  adapte ce chemin selon ton projet
import app.api.auth as auth_module
from app.dependencies import AccessTokenBearer

AUTH = "/auth"


def test_logout_success(client, monkeypatch):
    async def fake_access_call(self, request: Request):
        return {"jti": "JTI_TEST"}

    monkeypatch.setattr(AccessTokenBearer, "__call__", fake_access_call)

    blocklist_mock = AsyncMock()
    monkeypatch.setattr(auth_module, "add_jti_to_blocklist", blocklist_mock)

    resp = client.get(
        f"{AUTH}/logout",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 200, resp.text

    data = resp.json()
    assert "message" in data

    blocklist_mock.assert_awaited_once_with("JTI_TEST")

    set_cookie = (resp.headers.get("set-cookie") or "").lower()
    assert "refresh_token" in set_cookie


def test_logout_without_token(client):
    resp = client.get(f"{AUTH}/logout")
    assert resp.status_code in (401, 403), resp.text


def test_logout_blacklisted_token(client, monkeypatch):
    async def fake_access_call(self, request: Request):
        raise HTTPException(status_code=401, detail="Token revoked")

    monkeypatch.setattr(AccessTokenBearer, "__call__", fake_access_call)

    resp = client.get(
        f"{AUTH}/logout",
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 401, resp.text
    assert "Token revoked" in resp.text