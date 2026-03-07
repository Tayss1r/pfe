# tests/test_refresh.py
#
from datetime import datetime, timedelta
from unittest.mock import Mock

import app.api.auth as auth_module
from app.dependencies import RefreshTokenBearer

AUTH = "/auth"


def test_refresh_success(client, fastapi_app, monkeypatch):
    def override_refresh():
        return {
            "exp": int((datetime.now() + timedelta(minutes=5)).timestamp()),
            "user": {"email": "u@example.com", "user_uid": "1", "roles": ["admin"]},
        }

    fastapi_app.dependency_overrides[RefreshTokenBearer] = override_refresh
    monkeypatch.setattr(auth_module, "create_access_token", Mock(return_value="NEW_ACCESS"))

    resp = client.get(f"{AUTH}/refresh_token")
    assert resp.status_code == 200, resp.text
    assert resp.json()["access_token"] == "NEW_ACCESS"