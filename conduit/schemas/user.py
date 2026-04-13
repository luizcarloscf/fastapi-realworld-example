from typing import Annotated

from pydantic import BaseModel, EmailStr, SecretStr, WrapValidator

from conduit.schemas.utils import check_not_none_if_set, normalize_to_none


class UserData(BaseModel):
    email: EmailStr
    username: str
    token: str
    bio: str | None = None
    image: str | None = None


class UserResponse(BaseModel):
    user: UserData


class UserRegistration(BaseModel):
    email: Annotated[
        EmailStr,
        WrapValidator(check_not_none_if_set),
    ]
    username: Annotated[
        str,
        WrapValidator(check_not_none_if_set),
    ]
    password: Annotated[
        SecretStr,
        WrapValidator(check_not_none_if_set),
    ]


class UserRegistrationRequest(BaseModel):
    user: UserRegistration


class UserLogin(BaseModel):
    email: Annotated[
        EmailStr,
        WrapValidator(check_not_none_if_set),
    ]
    password: Annotated[
        SecretStr,
        WrapValidator(check_not_none_if_set),
    ]


class UserLoginRequest(BaseModel):
    user: UserLogin


class UserUpdate(BaseModel):
    email: Annotated[
        EmailStr | None,
        WrapValidator(check_not_none_if_set),
    ] = None
    username: Annotated[
        str | None,
        WrapValidator(check_not_none_if_set),
    ] = None
    password: Annotated[
        SecretStr | None,
        WrapValidator(check_not_none_if_set),
    ] = None
    bio: Annotated[
        str | None,
        WrapValidator(normalize_to_none),
    ] = None
    image: Annotated[
        str | None,
        WrapValidator(normalize_to_none),
    ] = None


class UserUpdateRequest(BaseModel):
    user: UserUpdate
