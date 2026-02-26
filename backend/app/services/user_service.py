from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from ..db.models import User
from ..schemas.user_schemas import UserCreate

from ..utils import hash


class UserService:
    @staticmethod
    async def get_user_by_email(email: EmailStr, session: AsyncSession):
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def user_exists(email: EmailStr, session: AsyncSession):
        return await UserService.get_user_by_email(email, session) is not None

    @staticmethod
    async def create_user(user: UserCreate, session: AsyncSession):
        user_dict = user.model_dump() # convert Pydantic to SQLAlchemy model
        new_user = User(**user_dict)
        new_user.password = hash(user_dict['password'])

        session.add(new_user)
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
