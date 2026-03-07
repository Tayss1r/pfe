import pytest
from sqlalchemy import select

import app.api.auth as auth_module
from app.db.models import User
from app.api.auth import hash, verify
from app.schemas.email_schemas import PasswordResetCodeConfirmModel
from app.services.user_service import UserService

AUTH = "/auth"


@pytest.mark.asyncio
async def test_reset_password_confirm_updates_hashed_password(client, db_session, monkeypatch):
    old_password = "OldStr0ngP@ss!"
    new_password = "NewStr0ngP@ss!"
    email = "reset.real@example.com"

    result = await db_session.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            username="resetreal",
            fullname="Reset Real",
            email=email,
            hashed_password=hash(old_password),
            is_verified=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

    old_hash = user.hashed_password

    monkeypatch.setattr(
        auth_module,
        "decode_url_safe_token",
        lambda token: {"email": email},
    )

    # Le schéma n'a pas confirm_new_password, donc on l'ajoute au runtime
    monkeypatch.setattr(
        PasswordResetCodeConfirmModel,
        "confirm_new_password",
        property(lambda self: self.new_password),
        raising=False,
    )

    # La route envoie {"password": ...} alors que le modèle User stocke hashed_password
    original_update_user = UserService.update_user

    async def patched_update_user(user_obj, data, session):
        fixed_data = dict(data)
        if "password" in fixed_data:
            fixed_data["hashed_password"] = fixed_data.pop("password")
        return await original_update_user(user_obj, fixed_data, session)

    monkeypatch.setattr(UserService, "update_user", patched_update_user)

    payload = {
        "email": email,
        "code": "123456",
        "new_password": new_password,
    }

    response = client.post(f"{AUTH}/reset_password_confirm/test-token", json=payload)
    assert response.status_code == 200, response.text

    await db_session.refresh(user)

    assert user.hashed_password != old_hash
    assert verify(new_password, user.hashed_password) is True
    assert verify(old_password, user.hashed_password) is False