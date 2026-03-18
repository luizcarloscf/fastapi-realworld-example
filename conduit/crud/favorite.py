from sqlmodel import select, delete, exists
from sqlmodel.ext.asyncio.session import AsyncSession

from conduit.models import Article, User, Favorite


async def favorite_article(
    session: AsyncSession,
    user: User,
    article: Article,
) -> None:
    favorite_db = Favorite(
        user_id=user.id,
        article_id=article.id,
    )
    session.add(favorite_db)
    await session.commit()


async def unfavorite_article(
    session: AsyncSession,
    user: User,
    article: Article,
) -> None:
    query = delete(Favorite).where(
        (Favorite.user_id == user.id) & (Favorite.article_id == article.id),
    )
    await session.exec(query)
    await session.commit()


async def is_favorited(
    *,
    session: AsyncSession,
    user: User,
    article: Article,
) -> bool:
    query = select(
        exists().where(
            (Favorite.user_id == user.id) & (Favorite.article_id == article.id),
        ),
    )
    result = await session.exec(query)
    return result.one()


async def get_favorites_by_article_id(
    session: AsyncSession,
    article_id: int,
) -> int:
    query = select(Favorite).where(
        Favorite.article_id == article_id,
    )
    result = await session.exec(query)
    return result.all()


async def delete_favorites_by_article_id(
    session: AsyncSession,
    article_id: int,
) -> None:
    query = delete(Favorite).where(
        Favorite.article_id == article_id,
    )
    await session.exec(query)
