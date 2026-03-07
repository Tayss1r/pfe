import pytest
from sqlalchemy import select

from app.db.models import User
from app.utils import hash

AUTH = "/auth"


@pytest.mark.asyncio
async def test_login_success_real_user(client, db_session):
    existing = await db_session.execute(
        select(User).where(User.email == "login.real@example.com")
    )
    user = existing.scalar_one_or_none()

    if user is None:
        user = User(
            username="loginreal",
            fullname="Login Real",
            email="login.real@example.com",
            hashed_password=hash("Str0ngP@ssw0rd!"),
            is_verified=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

    payload = {
        "email": "login.real@example.com",
        "password": "Str0ngP@ssw0rd!",
    }

    response = client.post(f"{AUTH}/login", json=payload)
    assert response.status_code == 200, response.text

    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "login.real@example.com"

    cookies = response.cookies
    assert cookies.get("refresh_token") is not None


@pytest.mark.asyncio
async def test_login_wrong_password_real_user(client, db_session):
    existing = await db_session.execute(
        select(User).where(User.email == "wrongpass.real@example.com")
    )
    user = existing.scalar_one_or_none()

    if user is None:
        user = User(
            username="wrongpassreal",
            fullname="Wrong Pass Real",
            email="wrongpass.real@example.com",
            hashed_password=hash("Str0ngP@ssw0rd!"),
            is_verified=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

    payload = {
        "email": "wrongpass.real@example.com",
        "password": "BadPassword123!",
    }

    response = client.post(f"{AUTH}/login", json=payload)
    assert response.status_code == 400, response.text


@pytest.mark.asyncio
async def test_login_nonexistent_user_real(client):
    payload = {
        "email": "doesnotexist.real@example.com",
        "password": "Str0ngP@ssw0rd!",
    }

    response = client.post(f"{AUTH}/login", json=payload)
    assert response.status_code == 400, response.text


@pytest.mark.asyncio
async def test_login_unverified_user_real(client, db_session):
    existing = await db_session.execute(
        select(User).where(User.email == "unverified.real@example.com")
    )
    user = existing.scalar_one_or_none()

    if user is None:
        user = User(
            username="unverifiedreal",
            fullname="Unverified Real",
            email="unverified.real@example.com",
            hashed_password=hash("Str0ngP@ssw0rd!"),
            is_verified=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

    payload = {
        "email": "unverified.real@example.com",
        "password": "Str0ngP@ssw0rd!",
    }

    response = client.post(f"{AUTH}/login", json=payload)
    assert response.status_code == 403, response.text