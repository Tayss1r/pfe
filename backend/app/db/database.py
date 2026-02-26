from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from sqlalchemy.orm import DeclarativeBase
from ..core.config import settings

SQLALCHEMY_DATABASE_URL = settings.database_url

# creation du pont entre python et db
async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False, pool_pre_ping=True)

# Factory to create session each time to prevent overlap requests (fastpi async)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


# the base class for the ORM models
class Base(DeclarativeBase):
    pass


# dependency to inject into the endpoint
async def get_session():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
