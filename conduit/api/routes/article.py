from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from slugify import slugify
from starlette import status

import conduit.crud.article as crud_article
import conduit.crud.favorite as crud_favorite
import conduit.crud.tag as crud_tag
import conduit.crud.comment as crud_comment
from conduit.api.deps import (
    CurrentOptionalUser,
    CurrentUser,
    SessionDB,
)
from conduit.schemas.article import (
    ArticleData,
    ArticleRegisterRequest,
    ArticleResponse,
    ArticlesResponse,
    ArticleUpdateRequest,
)
from conduit.schemas.profile import ProfileData

router = APIRouter()


@router.get(
    path="/articles",
    tags=["articles"],
    response_model=ArticlesResponse,
    summary="List articles with optional filters.",
)
async def list_articles(
    session: SessionDB,
    current_user: CurrentOptionalUser,
    tag: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    favorited: Optional[str] = Query(None),
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
) -> ArticlesResponse:
    return ArticlesResponse(
        articles=[],
        articles_count=0,
    )


@router.get(
    path="/articles/feed",
    tags=["articles"],
    response_model=ArticlesResponse,
    summary="Get articles from followed users.",
)
async def feed_articles(
    session: SessionDB,
    current_user: CurrentUser,
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
) -> ArticlesResponse:
    return ArticlesResponse(
        articles=[],
        articles_count=0,
    )


@router.post(
    path="/articles",
    tags=["articles"],
    response_model=ArticleResponse,
    summary="Create new article.",
)
async def create_article(
    session: SessionDB,
    current_user: CurrentUser,
    article_register_request: ArticleRegisterRequest,
) -> ArticleResponse:
    article_register = article_register_request.article
    maybe_article = await crud_article.get_article_by_slug(
        session=session,
        slug=slugify(article_register.title),
    )
    if maybe_article:
        raise HTTPException(
            status_code=422,
            detail="Article with same title already created.",
        )
    article_db = await crud_article.create_article(
        session=session,
        request=article_register,
        author_id=current_user.id,
    )

    await crud_tag.create_tags_for_article(
        session=session,
        article_id=article_db.id,
        tag_names=article_register.tag_list,
    )
    return ArticleResponse(
        article=ArticleData(
            slug=article_db.slug,
            title=article_db.title,
            description=article_db.description,
            body=article_db.body,
            author=ProfileData(
                username=current_user.username,
                bio=current_user.bio,
                image=current_user.image,
            ),
            tag_list=article_register.tag_list,
            favorited=False,
            favorites_count=0,
            created_at=article_db.created_at,
            updated_at=article_db.updated_at,
        )
    )


@router.get(
    path="/articles/{slug}",
    tags=["articles"],
    response_model=ArticleResponse,
    summary="Get article by slug.",
)
async def get_article(
    slug: str,
    session: SessionDB,
    current_user: CurrentOptionalUser,
) -> ArticleResponse:
    response = await crud_article.get_article_author_tags_favorite(
        session=session,
        article_slug=slug,
        current_user_id=current_user.id if current_user else 0,
    )
    if not response:
        raise HTTPException(
            status_code=404,
            detail=f"Article with slug '{slug}' not found.",
        )
    (
        article_db,
        author_db,
        following,
        favorites_count,
        favorited,
        tags_string,
    ) = response
    return ArticleResponse(
        article=ArticleData(
            slug=article_db.slug,
            title=article_db.title,
            description=article_db.description,
            body=article_db.body,
            author=ProfileData(
                username=author_db.username,
                bio=author_db.bio,
                image=author_db.image,
                following=following,
            ),
            tag_list=tags_string.split(",") if tags_string else [],
            favorited=favorited,
            favorites_count=favorites_count,
            created_at=article_db.created_at,
            updated_at=article_db.updated_at,
        )
    )


@router.put(
    path="/articles/{slug}",
    tags=["articles"],
    response_model=ArticleResponse,
    summary="Update article.",
)
async def update_article(
    slug: str,
    session: SessionDB,
    current_user: CurrentUser,
    article_update_request: ArticleUpdateRequest,
) -> ArticleResponse:
    response = await crud_article.get_article_author_tags_favorite(
        session=session,
        article_slug=slug,
        current_user_id=current_user.id,
    )
    if not response:
        raise HTTPException(
            status_code=404,
            detail=f"Article with slug '{slug}' not found.",
        )
    (
        article_db,
        author_db,
        following,
        favorites_count,
        favorited,
        tags_string,
    ) = response
    if article_db.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail=f"User '{current_user.username}' is not the author of the article with slug '{slug}'.",
        )
    article_db = await crud_article.update_article(
        session=session,
        article=article_db,
        request=article_update_request.article,
    )
    return ArticleResponse(
        article=ArticleData(
            slug=article_db.slug,
            title=article_db.title,
            description=article_db.description,
            body=article_db.body,
            author=ProfileData(
                username=author_db.username,
                bio=author_db.bio,
                image=author_db.image,
                following=following,
            ),
            tag_list=tags_string.split(",") if tags_string else [],
            favorited=favorited,
            favorites_count=favorites_count,
            created_at=article_db.created_at,
            updated_at=article_db.updated_at,
        )
    )


@router.delete(
    path="/articles/{slug}",
    tags=["articles"],
    summary="Delete article.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_article(
    slug: str,
    session: SessionDB,
    current_user: CurrentUser,
) -> None:
    db_article = await crud_article.get_article_by_slug(
        session=session,
        slug=slug,
    )
    if not db_article:
        raise HTTPException(
            status_code=404,
            detail=f"Article with slug '{slug}' not found.",
        )
    if db_article.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail=f"User '{current_user.username}' is not the author of the article with slug '{slug}'.",
        )
    await crud_article.delete_article(
        session=session,
        article=db_article,
    )


@router.post(
    path="/articles/{slug}/favorite",
    tags=["articles"],
    response_model=ArticleResponse,
    summary="Favorite an article.",
)
async def favorite_article(
    slug: str,
    session: SessionDB,
    current_user: CurrentUser,
) -> ArticleResponse:
    response = await crud_article.get_article_author_tags_favorite(
        session=session,
        article_slug=slug,
        current_user_id=current_user.id,
    )
    if response is None:
        raise HTTPException(
            status_code=404,
            detail=f"Article with slug '{slug}' not found.",
        )
    (
        article_db,
        author_db,
        following,
        favorites_count,
        favorited,
        tags_string,
    ) = response
    if favorited:
        raise HTTPException(
            status_code=422,
            detail=f"Article with slug '{slug}' already favorited by user '{current_user.username}'.",
        )
    await crud_favorite.favorite_article(
        session=session,
        user=current_user,
        article=article_db,
    )
    return ArticleResponse(
        article=ArticleData(
            slug=article_db.slug,
            title=article_db.title,
            description=article_db.description,
            body=article_db.body,
            author=ProfileData(
                username=author_db.username,
                bio=author_db.bio,
                image=author_db.image,
                following=following,
            ),
            tag_list=tags_string.split(",") if tags_string else [],
            favorited=True,
            favorites_count=favorites_count + 1,
            created_at=article_db.created_at,
            updated_at=article_db.updated_at,
        ),
    )


@router.delete(
    path="/articles/{slug}/favorite",
    tags=["articles"],
    response_model=ArticleResponse,
    summary="Unfavorite an article.",
)
async def unfavorite_article(
    slug: str,
    session: SessionDB,
    current_user: CurrentUser,
) -> ArticleResponse:
    response = await crud_article.get_article_author_tags_favorite(
        session=session,
        article_slug=slug,
        current_user_id=current_user.id,
    )
    if response is None:
        raise HTTPException(
            status_code=404,
            detail=f"Article with slug '{slug}' not found.",
        )
    (
        article_db,
        user_db,
        following,
        favorites_count,
        favorited,
        tags_string,
    ) = response

    if not favorited:
        raise HTTPException(
            status_code=422,
            detail=f"Article with slug '{slug}' not favorited by user '{current_user.username}'.",
        )
    await crud_favorite.unfavorite_article(
        session=session,
        user=current_user,
        article=article_db,
    )

    return ArticleResponse(
        article=ArticleData(
            slug=article_db.slug,
            title=article_db.title,
            description=article_db.description,
            body=article_db.body,
            author=ProfileData(
                username=user_db.username,
                bio=user_db.bio,
                image=user_db.image,
                following=following,
            ),
            tag_list=tags_string.split(",") if tags_string else [],
            favorited=False,
            favorites_count=(
                favorites_count - 1 if favorited else favorites_count
            ),
            created_at=article_db.created_at,
            updated_at=article_db.updated_at,
        ),
    )
