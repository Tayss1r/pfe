from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from ..db.models import User, Role
from ..schemas.user_schemas import UserCreate

from ..utils import hash


class UserService:
    @staticmethod
    async def get_user_by_email(email: EmailStr, session: AsyncSession):
        stmt = (
            select(User)
            .options(selectinload(User.roles)) # Eager load roles to avoid lazy loading issues
            .where(User.email == email)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def user_exists(email: EmailStr, session: AsyncSession):
        return await UserService.get_user_by_email(email, session) is not None

    @staticmethod
    async def create_user(user: UserCreate, session: AsyncSession):
        user_dict = user.model_dump() # convert Pydantic to SQLAlchemy model

        # Extract password and role (handle separately)
        plain_password = user_dict.pop('password')
        role_name = user_dict.pop('role')
        hashed_pwd = hash(plain_password)

        # Create user with hashed password (without role)
        new_user = User(**user_dict, hashed_password=hashed_pwd)

        session.add(new_user)
        await session.flush()

        # Fetch or create the role and assign it
        stmt = select(Role).where(Role.name == role_name)
        result = await session.execute(stmt)
        role = result.scalar_one_or_none()

        if role:
            new_user.roles.append(role)

        await session.commit()
        await session.refresh(new_user)

        return new_user

    @staticmethod
    async def update_user(user: User, update_data: dict, session: AsyncSession):
        """Update user attributes with the provided data dictionary"""
        for key, value in update_data.items():
            setattr(user, key, value)

        await session.commit()
        await session.refresh(user)

        return user
