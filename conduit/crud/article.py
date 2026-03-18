from secrets import token_urlsafe
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


def new_slug(title: str) -> str:
    slug = slugify(text=title, max_length=24, lowercase=True)
    unique_code = token_urlsafe(16)
    return f"{slug}-{unique_code.lower()}"


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
        slug=new_slug(request.title),
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
) -> Article:
    article_data = request.model_dump(exclude_unset=True)
    article.sqlmodel_update(article_data)
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


async def get_article_from_followed_authors(
    session: AsyncSession,
    current_user_id: Optional[int],
    limit: int,
    offset: int,
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
        .join(User, Article.author_id == User.id)
        .join(ArticleTag, Article.id == ArticleTag.article_id, isouter=True)
        .join(Tag, Tag.id == ArticleTag.tag_id, isouter=True)
        .filter(
            exists().where(
                (Follower.follower_id == current_user_id)
                & (Follower.following_id == Article.author_id)
            )
        )
        .group_by(Article, User)
        .limit(limit)
        .offset(offset)
        .order_by(Article.created_at.desc())
    )
    result = await session.exec(query)
    return result.all()


async def count_article_from_followed_authors(
    session: AsyncSession,
    current_user_id: Optional[int],
) -> int:
    if current_user_id is None:
        current_user_id = 0
    query = (
        select(func.count(Article.id))
        .select_from(Article)
        .filter(
            exists().where(
                (Follower.follower_id == current_user_id)
                & (Follower.following_id == Article.author_id)
            )
        )
    )
    result = await session.exec(query)
    return int(result.one())


async def get_articles_with_filters(
    session: AsyncSession,
    current_user_id: Optional[int],
    tag: Optional[str],
    author: Optional[str],
    favorited: Optional[str],
    limit: int,
    offset: int,
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
        .join(User, Article.author_id == User.id)
        .join(ArticleTag, Article.id == ArticleTag.article_id, isouter=True)
        .join(Tag, Tag.id == ArticleTag.tag_id, isouter=True)
        .group_by(Article, User)
    )
    if tag:
        query = query.filter(Tag.name == tag)
    if author:
        query = query.filter(User.username == author)
    if favorited:
        query = query.filter(
            exists().where(
                (User.username == favorited)
                & (Favorite.user_id == User.id)
                & (Favorite.article_id == Article.id),
            )
        )
    query = (
        query.limit(limit).offset(offset).order_by(Article.created_at.desc())
    )
    result = await session.exec(query)
    return result.all()


async def count_articles_with_filters(
    session: AsyncSession,
    tag: Optional[str],
    author: Optional[str],
    favorited: Optional[str],
) -> int:
    query = select(func.count(Article.id)).select_from(Article)
    if tag:
        query = query.join(ArticleTag).join(Tag).filter(Tag.name == tag)
    if author:
        query = query.join(User).filter(User.username == author)
    if favorited:
        query = (
            query.join(Favorite).join(User).filter(User.username == favorited)
        )
    result = await session.exec(query)
    return int(result.one())
