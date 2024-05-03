from typing import Optional, Annotated

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


from conduit.schemas.user import UserModelView
from conduit.schemas.profile import Profile


class ArticleModelView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    description: str
    body: str
    author_id: int
    created_at: datetime
    updated_at: datetime
    author: UserModelView


class NewArticleRequest(BaseModel):
    title: str
    description: str
    body: str


class Article(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, populate_by_name=True, alias_generator=to_camel
    )

    author: Profile
    title: str
    slug: str
    body: str
    description: str
    created_at: datetime
    updated_at: datetime


class SingleArticleResponse(BaseModel):
    article: Article
