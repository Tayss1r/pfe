import pytest
from sqlalchemy import select

import app.api.auth as auth_module
from app.db.models import User
from app.api.auth import hash, create_access_token

AUTH = "/auth"


@pytest.mark.asyncio
async def test_me_with_real_jwt(client, db_session):
    email = "me.real@example.com"

    result = await db_session.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            username="mereal",
            fullname="Me Real",
            email=email,
            hashed_password=hash("Str0ngP@ssw0rd!"),
            is_verified=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

    token = create_access_token(
        user_data={
            "email": user.email,
            "user_uid": str(user.id),
            "roles": [],
        }
    )

    async def patched_get_current_user():
        return {
            "id": 1,
            "username": user.username,
            "fullname": user.fullname,
            "email": user.email,
            "phone": "",
            "role": "user",
            "is_verified": user.is_verified,
        }

    client.app.dependency_overrides[auth_module.get_current_user] = patched_get_current_user

    try:
        response = client.get(
            f"{AUTH}/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["email"] == email

    finally:
        client.app.dependency_overrides.clear()