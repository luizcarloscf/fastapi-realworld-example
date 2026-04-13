from sqlmodel import delete
from sqlmodel.ext.asyncio.session import AsyncSession

from conduit.models import Favorite


async def favorite_article(
    *,
    session: AsyncSession,
    user_id: int,
    article_id: int,
) -> None:
    favorite_db = Favorite(user_id=user_id, article_id=article_id)
    session.add(favorite_db)
    await session.commit()


async def unfavorite_article(
    *,
    session: AsyncSession,
    user_id: int,
    article_id: int,
) -> None:
    query = delete(Favorite).where(
        (Favorite.user_id == user_id) & (Favorite.article_id == article_id),
    )
    await session.exec(query)
    await session.commit()
