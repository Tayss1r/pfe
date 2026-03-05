from pydantic import EmailStr
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db.models import User, Role, user_role_table
from ..schemas.user_schemas import UserCreate
from ..utils import hash


class UserService:

    @staticmethod
    async def get_user_by_email(email: EmailStr, session: AsyncSession):
        stmt = (
            select(User)
            .options(selectinload(User.roles))
            .where(User.email == email)
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def user_exists(email: EmailStr, session: AsyncSession):
        stmt = select(User.id).where(User.email == email)
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def create_user(user: UserCreate, session: AsyncSession):

        data = user.model_dump()

        plain_password = data.pop("password")
        hashed_pwd = hash(plain_password)

        new_user = User(**data, hashed_password=hashed_pwd)

        session.add(new_user)
        await session.flush()  # ensures new_user.id is generated

        role_stmt = select(Role.id).where(Role.name == "technicien")
        role_result = await session.execute(role_stmt)
        role_id = role_result.scalar_one_or_none()

        if role_id:
            # Insert directly into association table to avoid lazy-loading the relationship
            await session.execute(
                insert(user_role_table).values(user_id=new_user.id, role_id=role_id)
            )

        await session.commit()

        # Always reload entity with eager relationships
        stmt = (
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == new_user.id)
        )

        result = await session.execute(stmt)
        user_with_roles = result.scalar_one()

        return user_with_roles

    @staticmethod
    async def update_user(user: User, update_data: dict, session: AsyncSession):

        for key, value in update_data.items():
            setattr(user, key, value)

        await session.commit()

        stmt = (
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user.id)
        )

        result = await session.execute(stmt)
        updated_user = result.scalar_one()

        return updated_user