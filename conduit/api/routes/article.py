import logging

from fastapi import APIRouter, Query, status

import conduit.services.article as article_service
import conduit.services.favorite as favorite_service
import conduit.services.tag as tag_service
from conduit.api.dependencies import (
    CurrentOptionalUser,
    CurrentUser,
    SessionDB,
)
from conduit.exceptions import (
    ArticleAlreadyFavoritedException,
    ArticleNotAuthorException,
    ArticleNotFavoritedException,
    ArticleNotFoundException,
)
from conduit.schemas.article import (
    ArticleData,
    ArticleDataComplete,
    ArticleRegisterRequest,
    ArticleResponse,
    ArticlesResponse,
    ArticleUpdateRequest,
)
from conduit.schemas.profile import ProfileData

router = APIRouter()
log = logging.getLogger("conduit.api.articles")


@router.get(
    path="/articles",
    tags=["articles"],
    response_model=ArticlesResponse,
    summary="List articles with optional filters.",
    status_code=status.HTTP_200_OK,
)
async def list_articles(
    session: SessionDB,
    current_user: CurrentOptionalUser,
    tag: str | None = Query(None),
    author: str | None = Query(None),
    favorited: str | None = Query(None),
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
) -> ArticlesResponse:
    response = await article_service.get_articles_with_filters(
        session=session,
        current_user_id=current_user.id if current_user else None,
        tag=tag,
        author=author,
        favorited=favorited,
        limit=limit,
        offset=offset,
    )
    article_count = await article_service.count_articles_with_filters(
        session=session,
        tag=tag,
        author=author,
        favorited=favorited,
    )
    return ArticlesResponse(
        articles=[
            ArticleData(
                slug=article_db.slug,
                title=article_db.title,
                description=article_db.description,
                author=ProfileData(
                    username=user_db.username,
                    bio=user_db.bio,
                    image=user_db.image,
                    following=following,
                ),
                tag_list=sorted(tags_string.split(",")) if tags_string else [],
                favorited=favorited,
                favorites_count=favorites_count,
                created_at=article_db.created_at,
                updated_at=article_db.updated_at,
            )
            for article_db, user_db, following, favorites_count, favorited, tags_string in response
        ],
        articles_count=article_count,
    )


@router.get(
    path="/articles/feed",
    tags=["articles"],
    response_model=ArticlesResponse,
    summary="Get articles from followed users.",
    status_code=status.HTTP_200_OK,
)
async def feed_articles(
    session: SessionDB,
    current_user: CurrentUser,
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
) -> ArticlesResponse:
    response = await article_service.get_articles_from_followed_authors(
        session=session,
        current_user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    articles_count = await article_service.count_articles_from_followed_authors(
        session=session,
        current_user_id=current_user.id,
    )
    return ArticlesResponse(
        articles=[
            ArticleData(
                slug=article_db.slug,
                title=article_db.title,
                description=article_db.description,
                author=ProfileData(
                    username=user_db.username,
                    bio=user_db.bio,
                    image=user_db.image,
                    following=following,
                ),
                tag_list=sorted(tags_string.split(",")) if tags_string else [],
                favorited=favorited,
                favorites_count=favorites_count,
                created_at=article_db.created_at,
                updated_at=article_db.updated_at,
            )
            for article_db, user_db, following, favorites_count, favorited, tags_string in response
        ],
        articles_count=articles_count,
    )


@router.post(
    path="/articles",
    tags=["articles"],
    response_model=ArticleResponse,
    summary="Create new article.",
    status_code=status.HTTP_201_CREATED,
)
async def create_article(
    session: SessionDB,
    current_user: CurrentUser,
    article_request: ArticleRegisterRequest,
) -> ArticleResponse:
    article = article_request.article
    article_db = await article_service.create_article(
        session=session,
        request=article,
        author_id=current_user.id,
    )
    if article.tag_list:
        await tag_service.create_tags_for_article(
            session=session,
            article_id=article_db.id,
            tag_names=article.tag_list,
        )
    return ArticleResponse(
        article=ArticleDataComplete(
            slug=article_db.slug,
            title=article_db.title,
            description=article_db.description,
            body=article_db.body,
            author=ProfileData(
                username=current_user.username,
                bio=current_user.bio,
                image=current_user.image,
            ),
            tag_list=(article.tag_list if article.tag_list else []),
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
    status_code=status.HTTP_200_OK,
)
async def get_article(
    slug: str,
    session: SessionDB,
    current_user: CurrentOptionalUser,
) -> ArticleResponse:
    response = await article_service.get_article_author_tags_favorite(
        session=session,
        article_slug=slug,
        current_user_id=current_user.id if current_user else 0,
    )
    if not response:
        raise ArticleNotFoundException()
    (
        article_db,
        author_db,
        following,
        favorites_count,
        favorited,
        tags_string,
    ) = response
    return ArticleResponse(
        article=ArticleDataComplete(
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
    status_code=status.HTTP_200_OK,
)
async def update_article(
    slug: str,
    session: SessionDB,
    current_user: CurrentUser,
    article_request: ArticleUpdateRequest,
) -> ArticleResponse:
    article = article_request.article
    response = await article_service.get_article_author_tags_favorite(
        session=session,
        article_slug=slug,
        current_user_id=current_user.id,
    )
    if not response:
        raise ArticleNotFoundException()
    (
        article_db,
        author_db,
        following,
        favorites_count,
        favorited,
        tags_string,
    ) = response
    if article_db.author_id != current_user.id:
        raise ArticleNotAuthorException()

    if article.title or article.body or article.description:
        article_db = await article_service.update_article(
            session=session,
            article=article_db,
            request=article,
        )

    tags = tags_string.split(",") if tags_string else []
    if article.tag_list is not None:
        await tag_service.delete_tags_for_article(
            session=session,
            article_id=article_db.id,
        )
        if article.tag_list:
            await tag_service.create_tags_for_article(
                session=session,
                article_id=article_db.id,
                tag_names=article.tag_list,
            )
        tags = article.tag_list

    return ArticleResponse(
        article=ArticleDataComplete(
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
            tag_list=sorted(tags),
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
    db_article = await article_service.get_article_by_slug(
        session=session,
        slug=slug,
    )
    if not db_article:
        raise ArticleNotFoundException()
    if db_article.author_id != current_user.id:
        raise ArticleNotAuthorException()
    await article_service.delete_article(
        session=session,
        article=db_article,
    )


@router.post(
    path="/articles/{slug}/favorite",
    tags=["articles"],
    response_model=ArticleResponse,
    summary="Favorite an article.",
    status_code=status.HTTP_200_OK,
)
async def favorite_article(
    slug: str,
    session: SessionDB,
    current_user: CurrentUser,
) -> ArticleResponse:
    response = await article_service.get_article_author_tags_favorite(
        session=session,
        article_slug=slug,
        current_user_id=current_user.id,
    )
    if response is None:
        raise ArticleNotFoundException()
    (
        article_db,
        author_db,
        following,
        favorites_count,
        favorited,
        tags_string,
    ) = response
    if favorited:
        raise ArticleAlreadyFavoritedException()
    await favorite_service.favorite_article(
        session=session,
        user_id=current_user.id,
        article_id=article_db.id,
    )
    return ArticleResponse(
        article=ArticleDataComplete(
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
            tag_list=sorted(tags_string.split(",")) if tags_string else [],
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
    status_code=status.HTTP_200_OK,
)
async def unfavorite_article(
    slug: str,
    session: SessionDB,
    current_user: CurrentUser,
) -> ArticleResponse:
    response = await article_service.get_article_author_tags_favorite(
        session=session,
        article_slug=slug,
        current_user_id=current_user.id,
    )
    if response is None:
        raise ArticleNotFoundException()
    (
        article_db,
        user_db,
        following,
        favorites_count,
        favorited,
        tags_string,
    ) = response

    if not favorited:
        raise ArticleNotFavoritedException()

    await favorite_service.unfavorite_article(
        session=session,
        user_id=current_user.id,
        article_id=article_db.id,
    )
    favorites_count = favorites_count - 1 if favorited else favorites_count
    tags = sorted(tags_string.split(",")) if tags_string else []
    return ArticleResponse(
        article=ArticleDataComplete(
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
            tag_list=tags,
            favorited=False,
            favorites_count=favorites_count,
            created_at=article_db.created_at,
            updated_at=article_db.updated_at,
        ),
    )
