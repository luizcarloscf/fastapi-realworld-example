from typing import List, Annotated

from pydantic import BaseModel, ConfigDict, WrapValidator
from pydantic.alias_generators import to_camel


from conduit.schemas.profile import ProfileData
from conduit.schemas.utils import (
    DatetimeISOFormat,
    check_not_none_if_set,
)


class ArticleRegister(BaseModel):
    title: Annotated[
        str,
        WrapValidator(check_not_none_if_set),
    ]
    description: Annotated[
        str,
        WrapValidator(check_not_none_if_set),
    ]
    body: Annotated[
        str,
        WrapValidator(check_not_none_if_set),
    ]
    tag_list: Annotated[
        List[str],
        WrapValidator(check_not_none_if_set),
    ] = []

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class ArticleRegisterRequest(BaseModel):
    article: ArticleRegister


class ArticleUpdate(BaseModel):
    title: Annotated[
        str | None,
        WrapValidator(check_not_none_if_set),
    ] = None
    description: Annotated[
        str | None,
        WrapValidator(check_not_none_if_set),
    ] = None
    body: Annotated[
        str | None,
        WrapValidator(check_not_none_if_set),
    ] = None
    tag_list: Annotated[
        List[str] | None,
        WrapValidator(check_not_none_if_set),
    ] = None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


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
