from typing import Optional

from datetime import datetime
from pydantic import BaseModel, ConfigDict


from conduit.schemas.users import UserModelView
from conduit.schemas.profile import Profile


class ArticleModelView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    description: str
    body: str
    author_id: int
    author: UserModelView


class NewArticleRequest(BaseModel):
    title: str
    description: str
    body: str


class Article(BaseModel):
    author: Profile
    title: str
    slug: str
    body: str
    description: str


class SingleArticleResponse(BaseModel):
    article: Article
