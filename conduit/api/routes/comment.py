import logging

from fastapi import APIRouter, status

import conduit.services.comment as comment_service
import conduit.services.article as article_service
from conduit.api.dependencies import (
    SessionDB,
    CurrentUser,
    CurrentOptionalUser,
)
from conduit.schemas.comment import (
    CommentRegisterRequest,
    CommentData,
    CommentResponse,
    CommentsResponse,
)
from conduit.schemas.profile import ProfileData
from conduit.exceptions import (
    CommentNotFoundException,
    CommentNotAuthorException,
    ArticleNotFoundException,
)

router = APIRouter()
log = logging.getLogger("conduit.api.comments")


@router.post(
    path="/articles/{slug}/comments",
    tags=["comments"],
    response_model=CommentResponse,
    summary="Add comment to article.",
    status_code=status.HTTP_201_CREATED,
)
async def add_comment(
    slug: str,
    session: SessionDB,
    current_user: CurrentUser,
    comment_register: CommentRegisterRequest,
) -> CommentResponse:
    comment = comment_register.comment
    article = await article_service.get_article_by_slug(
        session=session,
        slug=slug,
    )
    if not article:
        raise ArticleNotFoundException()

    comment_db = await comment_service.create_comment(
        session=session,
        comment_body=comment.body,
        article_id=article.id,
        user_id=current_user.id,
    )
    return CommentResponse(
        comment=CommentData(
            id=comment_db.id,
            body=comment_db.body,
            author=ProfileData(
                username=current_user.username,
                bio=current_user.bio,
                image=current_user.image,
            ),
            created_at=comment_db.created_at,
            updated_at=comment_db.updated_at,
        )
    )


@router.get(
    path="/articles/{slug}/comments",
    tags=["comments"],
    response_model=CommentsResponse,
    summary="Get comments for article.",
    status_code=status.HTTP_200_OK,
)
async def get_comments(
    slug: str,
    session: SessionDB,
    current_user: CurrentOptionalUser,
) -> CommentsResponse:
    article = await article_service.get_article_by_slug(
        session=session,
        slug=slug,
    )
    if not article:
        raise ArticleNotFoundException()
    response = await comment_service.get_comments_and_users_by_article_id(
        session=session,
        article_id=article.id,
        current_user_id=current_user.id if current_user else None,
    )
    return CommentsResponse(
        comments=[
            CommentData(
                id=comment.id,
                body=comment.body,
                author=ProfileData(
                    username=user.username,
                    bio=user.bio,
                    image=user.image,
                    following=following,
                ),
                created_at=comment.created_at,
                updated_at=comment.updated_at,
            )
            for comment, user, following in response
        ]
    )


@router.delete(
    path="/articles/{slug}/comments/{comment_id}",
    tags=["comments"],
    summary="Delete comment.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    slug: str,
    comment_id: int,
    session: SessionDB,
    current_user: CurrentUser,
) -> None:
    article = await article_service.get_article_by_slug(
        session=session,
        slug=slug,
    )
    if not article:
        raise ArticleNotFoundException()

    comment = await comment_service.get_comment_by_id(
        session=session,
        comment_id=comment_id,
    )
    if not comment or comment.article_id != article.id:
        raise CommentNotFoundException()
    if comment.author_id != current_user.id:
        raise CommentNotAuthorException()

    await comment_service.delete_comment_by_id(
        session=session,
        comment_id=comment_id,
    )
