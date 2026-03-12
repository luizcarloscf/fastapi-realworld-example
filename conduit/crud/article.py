from typing import Optional, List, Tuple

from slugify import slugify
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from conduit.models import (
    Article,
    User,
    Tag,
)
from conduit.schemas.article import (
    ArticleRegister,
    ArticleUpdate,
)


async def get_article_by_slug(
    *,
    session: AsyncSession,
    slug: str,
) -> Optional[Article]:
    query = select(Article).where(
        Article.slug == slug,
    )
    result = await session.exec(query)
    return result.one_or_none()


async def get_article_and_user_by_slug(
    *,
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
    *,
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
    await session.flush()
    await session.commit()
    return instance


async def update_article(
    *,
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
    *,
    session: AsyncSession,
    article: Article,
) -> None:
    await session.delete(article)
    await session.commit()
