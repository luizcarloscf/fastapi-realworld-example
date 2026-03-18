from fastapi import APIRouter, HTTPException
from starlette import status

import conduit.crud.comment as crud_comment
import conduit.crud.article as crud_article
from conduit.api.deps import SessionDB, CurrentUser, CurrentOptionalUser
from conduit.schemas.comment import (
    CommentRegisterRequest,
    CommentData,
    CommentResponse,
    CommentsResponse,
)
from conduit.schemas.profile import ProfileData


router = APIRouter()


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
    comment: CommentRegisterRequest,
) -> CommentResponse:

    if not comment.comment.body:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Comment body cannot be empty.",
        )

    article = await crud_article.get_article_by_slug(
        session=session,
        slug=slug,
    )
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found.",
        )

    instance = await crud_comment.create_comment(
        session=session,
        comment_registration=comment.comment,
        article=article,
        user=current_user,
    )
    return CommentResponse(
        comment=CommentData(
            id=instance.id,
            body=instance.body,
            author=ProfileData(
                username=current_user.username,
                bio=current_user.bio,
                image=current_user.image,
            ),
            created_at=instance.created_at,
            updated_at=instance.updated_at,
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
    article = await crud_article.get_article_by_slug(
        session=session,
        slug=slug,
    )
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found.",
        )
    comments = await crud_comment.get_comments_and_users_by_article_id(
        session=session,
        article_id=article.id,
    )
    return CommentsResponse(
        comments=[
            CommentData(
                id=c.id,
                body=c.body,
                author=ProfileData(
                    username=u.username,
                    bio=u.bio,
                    image=u.image,
                ),
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c, u in comments
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
    article = await crud_article.get_article_by_slug(
        session=session,
        slug=slug,
    )
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found.",
        )

    comment = await crud_comment.get_comment_by_id(
        session=session,
        comment_id=comment_id,
    )
    if not comment or comment.article_id != article.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found.",
        )
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment.",
        )

    await crud_comment.delete_comment(
        session=session,
        comment=comment,
    )
