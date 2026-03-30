from typing import List, Optional, Tuple

from sqlmodel import delete, exists, select
from sqlmodel.ext.asyncio.session import AsyncSession

from conduit.models import Comment, Follower, User


async def create_comment(
    *,
    session: AsyncSession,
    comment_body: str,
    article_id: int,
    user_id: int,
) -> Comment:
    instance = Comment(
        body=comment_body,
        article_id=article_id,
        author_id=user_id,
    )
    session.add(instance)
    await session.commit()
    await session.refresh(instance)
    return instance


async def get_comments_and_users_by_article_id(
    *,
    session: AsyncSession,
    article_id: int,
    current_user_id: int | None = None,
) -> List[Tuple[Comment, User, bool]]:
    if current_user_id is None:
        current_user_id = 0
    query = (
        select(
            Comment,
            User,
            exists()
            .where(
                (Follower.follower_id == current_user_id)
                & (Follower.following_id == Comment.author_id)
            )
            .label("following"),
        )
        .where(
            Comment.article_id == article_id,
        )
        .join(User, Comment.author_id == User.id)
    )
    result = await session.exec(query)
    return result.all()


async def get_comment_by_id(
    *,
    session: AsyncSession,
    comment_id: int,
) -> Optional[Comment]:
    query = select(Comment).where(
        Comment.id == comment_id,
    )
    result = await session.exec(query)
    return result.one_or_none()


async def delete_comment_by_id(
    *,
    session: AsyncSession,
    comment_id: int,
) -> None:
    query = delete(Comment).where(
        (Comment.id == comment_id),
    )
    await session.exec(query)
    await session.commit()


async def delete_comments_by_article_id(
    *,
    session: AsyncSession,
    article_id: int,
) -> None:
    query = delete(Comment).where(
        (Comment.article_id == article_id),
    )
    await session.exec(query)
    await session.commit()
