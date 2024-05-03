import logging
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException
from opentelemetry import trace
from slugify import slugify

from conduit import crud
from conduit.api.deps import CurrentUserDep, SessionDep, TokenDep
from conduit.core.security import create_access_token
from conduit.schemas.article import (
    NewArticleRequest,
    SingleArticleResponse,
    Article,
    ArticleModelView,
)

router = APIRouter()
log = logging.getLogger("conduit.api.articles")
log.setLevel(level=logging.DEBUG)
tracer = trace.get_tracer(__name__)


@router.post(
    path="/articles",
    tags=["articles"],
    response_model=SingleArticleResponse,
    summary="Create new article.",
)
@tracer.start_as_current_span(name="POST /articles create_article")
async def create_article(
    session: SessionDep,
    current_user: CurrentUserDep,
    article: Annotated[NewArticleRequest, Body(embed=True)],
) -> SingleArticleResponse:
    log.info("Start POST /articles create_article")
    slug = slugify(article.title)
    maybe_article = crud.get_article_by_slug(session=session, slug=slug)
    if maybe_article:
        msg = "Article with same title already created."
        log.error(msg=msg)
        raise HTTPException(status_code=400, detail="msg")
    instance = crud.create_article(session=session, request=article, user=current_user)
    instance_view = ArticleModelView.model_validate(instance)
    return SingleArticleResponse(article=Article(**instance_view.model_dump()))
