from typing import List, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


from conduit.schemas.profile import ProfileData
from conduit.schemas.utils import DatetimeISOFormat


class ArticleRegister(BaseModel):
    title: str
    description: str
    body: str
    tag_list: List[str]

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class ArticleRegisterRequest(BaseModel):
    article: ArticleRegister


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    body: Optional[str] = None


class ArticleUpdateRequest(BaseModel):
    article: ArticleUpdate


class ArticleData(BaseModel):

    author: ProfileData
    title: str
    slug: str
    body: str
    description: str
    created_at: DatetimeISOFormat
    updated_at: DatetimeISOFormat
    tag_list: List[str]
    favorited: bool | None
    favorites_count: int

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class ArticleResponse(BaseModel):
    article: ArticleData


class ArticlesResponse(BaseModel):
    articles: List[ArticleData]
    articles_count: int

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
