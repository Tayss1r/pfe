import pytest
from sqlalchemy import select

from app.db.models import User
from app.utils import hash


@pytest.mark.asyncio
async def test_insert_user_directly_in_test_db(db_session):
    new_user = User(
        username="nouha_direct",
        fullname="Nouha Direct",
        email="nouha.direct@example.com",
        hashed_password=hash("Str0ngP@ssw0rd!"),
        is_verified=False,
    )

    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)

    result = await db_session.execute(
        select(User).where(User.email == "nouha.direct@example.com")
    )
    user = result.scalar_one_or_none()

    assert user is not None
    assert user.username == "nouha_direct"
    assert user.fullname == "Nouha Direct"
    assert user.email == "nouha.direct@example.com"
    assert user.is_verified is False
    assert user.hashed_password != "Str0ngP@ssw0rd!"
    assert user.hashed_password