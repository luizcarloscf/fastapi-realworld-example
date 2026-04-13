from typing import Annotated

from fastapi import Depends
from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession

from conduit.core.database import get_db
from conduit.core.security import HTTPTokenHeader
from conduit.core.settings import Settings, get_settings_cached
from conduit.exceptions import (
    InvalidCredentialsException,
    TokenExpiredException,
    TokenInvalidException,
    UserNotFoundException,
)
from conduit.models import User
from conduit.schemas.token import TokenPayload
from conduit.services import user as user_service

bearer = HTTPTokenHeader(raise_error=True, name="Authorization")
bearer_optional = HTTPTokenHeader(raise_error=False, name="Authorization")

Token = Annotated[
    str,
    Depends(bearer),
]
TokenOptional = Annotated[
    str | None,
    Depends(bearer_optional),
]
SettingsDep = Annotated[
    Settings,
    Depends(get_settings_cached),
]
SessionDB = Annotated[
    AsyncSession,
    Depends(get_db),
]


async def get_current_user(
    session: SessionDB,
    token: Token,
    settings: SettingsDep,
) -> User:
    try:
        payload = jwt.decode(
            token=token,
            key=settings.secret_key,
            algorithms=[settings.algorithm],
        )
        token_data = TokenPayload(**payload)
    except JWTError as ex:
        raise TokenInvalidException() from ex
    except ExpiredSignatureError as ex:
        raise TokenExpiredException() from ex
    except ValidationError as ex:
        raise InvalidCredentialsException() from ex
    user_db = await user_service.get_user_by_id(
        session=session,
        user_id=token_data.sub,
    )
    if not user_db:
        raise UserNotFoundException()
    return user_db


async def get_current_user_optional(
    session: SessionDB,
    token: TokenOptional,
    settings: SettingsDep,
) -> User | None:
    if not token:
        return None
    try:
        payload = jwt.decode(
            token=token,
            key=settings.secret_key,
            algorithms=[settings.algorithm],
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ExpiredSignatureError, ValidationError):
        return None
    user_db = await user_service.get_user_by_id(
        session=session,
        user_id=token_data.sub,
    )
    return user_db


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]
CurrentOptionalUser = Annotated[
    User | None,
    Depends(get_current_user_optional),
]
