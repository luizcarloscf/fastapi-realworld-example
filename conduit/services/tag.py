from typing import List, Sequence

from sqlmodel import col, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from conduit.models import ArticleTag, Tag


async def get_all_tags(
    *,
    session: AsyncSession,
) -> Sequence[Tag]:
    result = await session.exec(
        select(Tag),
    )
    return result.all()


async def get_tags_by_article_id(
    *,
    session: AsyncSession,
    article_id: int,
) -> Sequence[Tag]:
    query = (
        select(Tag)
        .join(ArticleTag, ArticleTag.tag_id == Tag.id)
        .where(ArticleTag.article_id == article_id)
    )
    result = await session.exec(query)
    return result.all()


async def create_tags_for_article(
    *,
    session: AsyncSession,
    tag_names: List[str],
    article_id: int,
) -> None:
    tags: list[Tag] = []
    if not tag_names:
        return

    query = select(Tag).where(
        col(Tag.name).in_(tag_names),
    )
    result = await session.exec(query)
    existing_tags = {tag.name: tag for tag in result.all()}
    for name in tag_names:
        tag = existing_tags.get(name)
        if not tag:
            tag = Tag(name=name)
            session.add(tag)
        tags.append(tag)
    await session.commit()

    for tag in tags:
        session.add(
            ArticleTag(
                article_id=article_id,
                tag_id=tag.id,
            )
        )
    await session.commit()


async def delete_tags_for_article(
    *,
    session: AsyncSession,
    article_id: int,
) -> None:
    query = delete(ArticleTag).where(
        (ArticleTag.article_id == article_id),
    )
    await session.exec(query)
    await session.commit()
