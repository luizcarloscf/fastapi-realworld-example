# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from sqlmodel.ext.asyncio.session import AsyncSession

# from sqlmodel.orm import DeclarativeBase, sessionmaker

from conduit.core.config import SETTINGS

ENGINE = create_async_engine(
    url=str(SETTINGS.DATABASE_URI),
    pool_size=10,
    max_overflow=20,
    pool_recycle=300,
)


class Base(DeclarativeBase):
    pass


AsyncSessionLocal = sessionmaker(
    bind=ENGINE,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
