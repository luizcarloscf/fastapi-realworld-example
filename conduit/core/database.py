from typing import Any

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from conduit.core.settings import get_settings_cached

SETTINGS = get_settings_cached()

ENGINE = create_async_engine(
    url=str(SETTINGS.DATABASE_URI),
    pool_size=10,
    max_overflow=20,
    pool_recycle=300,
)


AsyncSessionLocal = sessionmaker(
    bind=ENGINE,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> Any:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
