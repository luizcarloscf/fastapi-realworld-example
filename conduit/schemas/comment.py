from typing import Annotated, List

from pydantic import BaseModel, ConfigDict, WrapValidator
from pydantic.alias_generators import to_camel

from conduit.schemas.profile import ProfileData
from conduit.schemas.utils import DatetimeISOFormat, check_not_none_if_set


class CommentRegister(BaseModel):
    body: Annotated[
        str,
        WrapValidator(check_not_none_if_set),
    ]


class CommentRegisterRequest(BaseModel):
    comment: CommentRegister


class CommentData(BaseModel):
    id: int
    body: str
    author: ProfileData
    created_at: DatetimeISOFormat
    updated_at: DatetimeISOFormat

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class CommentResponse(BaseModel):
    comment: CommentData


class CommentsResponse(BaseModel):
    comments: List[CommentData]
