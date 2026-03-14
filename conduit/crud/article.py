from typing import Optional, Tuple

from slugify import slugify
from sqlmodel import func, select, exists
from sqlmodel.ext.asyncio.session import AsyncSession
from conduit.models import (
    Article,
    Follower,
    User,
    Tag,
    ArticleTag,
    Favorite,
)
from conduit.schemas.article import (
    ArticleRegister,
    ArticleUpdate,
)


async def get_article_by_slug(
    session: AsyncSession,
    slug: str,
) -> Optional[Article]:
    query = select(Article).where(
        Article.slug == slug,
    )
    result = await session.exec(query)
    return result.one_or_none()


async def get_article_and_user_by_slug(
    session: AsyncSession,
    slug: str,
) -> Optional[Tuple[Article, User]]:
    query = (
        select(Article, User)
        .where(Article.slug == slug)
        .join(User, Article.author_id == User.id)
    )
    result = await session.exec(query)
    return result.one_or_none()


async def create_article(
    session: AsyncSession,
    author_id: User,
    request: ArticleRegister,
) -> Article:

    instance = Article(
        slug=slugify(request.title),
        title=request.title,
        description=request.description,
        body=request.body,
        author_id=author_id,
    )
    session.add(instance)
    await session.commit()
    return instance


async def update_article(
    session: AsyncSession,
    article: Article,
    request: ArticleUpdate,
) -> None:
    if request.title is not None:
        article.title = request.title
    if request.description is not None:
        article.description = request.description
    if request.body is not None:
        article.body = request.body
    session.add(article)
    await session.commit()
    await session.refresh(article)
    return article


async def delete_article(
    session: AsyncSession,
    article: Article,
) -> None:
    await session.delete(article)
    await session.commit()


async def get_article_author_tags_favorite(
    session: AsyncSession,
    article_slug: str,
    current_user_id: Optional[int],
) -> Optional[Tuple[Article, User, bool, int, bool, str]]:
    if current_user_id is None:
        current_user_id = 0
    query = (
        select(
            Article,
            User,
            exists()
            .where(
                (Follower.follower_id == current_user_id)
                & (Follower.following_id == Article.author_id)
            )
            .label("following"),
            select(func.count(Favorite.article_id))
            .where(Favorite.article_id == Article.id)
            .scalar_subquery()
            .label("favorites_count"),
            exists()
            .where(
                (Favorite.user_id == current_user_id)
                & (Favorite.article_id == Article.id)
            )
            .label("favorited"),
            func.string_agg(Tag.name, ",").label("tags"),
        )
        .where(Article.slug == article_slug)
        .join(User, Article.author_id == User.id)
        .join(ArticleTag, Article.id == ArticleTag.article_id, isouter=True)
        .join(Tag, Tag.id == ArticleTag.tag_id, isouter=True)
        .group_by(Article, User)
    )
    result = await session.exec(query)
    return result.one_or_none()
