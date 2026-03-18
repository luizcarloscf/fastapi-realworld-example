from typing import Optional, List, Tuple

from sqlmodel import select, delete
from sqlmodel.ext.asyncio.session import AsyncSession

from conduit.models import Comment, User, Article
from conduit.schemas.comment import CommentRegister


async def create_comment(
    session: AsyncSession,
    comment_registration: CommentRegister,
    article: Article,
    user: User,
) -> Comment:
    instance = Comment(
        body=comment_registration.body,
        article_id=article.id,
        author_id=user.id,
    )
    session.add(instance)
    await session.commit()
    await session.refresh(instance)
    return instance


async def get_comments_and_users_by_article_id(
    session: AsyncSession,
    article_id: int,
) -> List[Tuple[Comment, User]]:
    query = (
        select(Comment, User)
        .where(
            Comment.article_id == article_id,
        )
        .join(User, Comment.author_id == User.id)
    )
    result = await session.exec(query)
    return result.all()


async def get_comment_by_id(
    session: AsyncSession,
    comment_id: int,
) -> Optional[Comment]:
    query = select(Comment).where(
        Comment.id == comment_id,
    )
    result = await session.exec(query)
    return result.one_or_none()


async def delete_comment(
    session: AsyncSession,
    comment: Comment,
) -> None:
    query = delete(Comment).where(
        (Comment.id == comment.id),
    )
    await session.exec(query)
    await session.commit()


async def delete_comments_by_article_id(
    session: AsyncSession,
    article_id: int,
) -> None:
    query = delete(Comment).where(
        (Comment.article_id == article_id),
    )
    await session.exec(query)
    await session.commit()
