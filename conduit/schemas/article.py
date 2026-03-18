from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel


from conduit.schemas.profile import ProfileData
from conduit.schemas.utils import DatetimeISOFormat


class ArticleRegister(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)
    tag_list: Optional[List[str]] = None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    @field_validator("tag_list", mode="before")
    @classmethod
    def check_not_none_if_set(cls, v):
        if v is None:
            raise ValueError(f"Field cannot be set to null")
        return v


class ArticleRegisterRequest(BaseModel):
    article: ArticleRegister


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    body: Optional[str] = None
    tag_list: Optional[List[str]] = None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    @field_validator("title", "description", "body", "tag_list", mode="before")
    @classmethod
    def check_not_none_if_set(cls, v):
        if v is None:
            raise ValueError(f"Field cannot be set to null")
        return v


class ArticleUpdateRequest(BaseModel):
    article: ArticleUpdate


class ArticleData(BaseModel):

    author: ProfileData
    title: str
    slug: str
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


class ArticleDataComplete(ArticleData):

    body: str


class ArticleResponse(BaseModel):
    article: ArticleDataComplete


class ArticlesResponse(BaseModel):
    articles: List[ArticleData]
    articles_count: int

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
