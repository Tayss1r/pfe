import pytest
from sqlalchemy import select

import app.api.auth as auth_module
from app.db.models import User

AUTH = "/auth"


@pytest.mark.asyncio
async def test_signup_creates_user_in_db(client, db_session, monkeypatch):
    sent_emails = []

    async def fake_store_email_verification_code(email: str, code: str):
        return None

    def fake_send_verification_code_email(user, code: str):
        sent_emails.append((user.email, code))

    monkeypatch.setattr(
        auth_module,
        "store_email_verification_code",
        fake_store_email_verification_code,
    )
    monkeypatch.setattr(
        auth_module,
        "send_verification_code_email",
        fake_send_verification_code_email,
    )

    payload = {
        "username": "nouha_test",
        "fullname": "Nouha Balloume",
        "email": "nouha.integration@example.com",
        "password": "Str0ngP@ssw0rd!",
    }

    response = client.post(f"{AUTH}/signup", json=payload)
    assert response.status_code == 201, response.text

    data = response.json()
    assert data["email"] == payload["email"]
    assert sent_emails

    result = await db_session.execute(
        select(User).where(User.email == payload["email"])
    )
    user = result.scalar_one_or_none()

    assert user is not None
    assert user.username == payload["username"]
    assert user.fullname == payload["fullname"]
    assert user.email == payload["email"]
    assert user.is_verified is False
    assert user.hashed_password != payload["password"]
    assert user.hashed_password