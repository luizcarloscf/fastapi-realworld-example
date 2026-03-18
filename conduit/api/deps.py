from typing import Annotated, Any, Optional

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.requests import Request
from starlette import status

from conduit.core.config import SETTINGS
from conduit.core.database import get_db
from conduit.models import User
from conduit.schemas.token import TokenPayload

SessionDB = Annotated[AsyncSession, Depends(get_db)]


class HTTPTokenHeader(APIKeyHeader):
    def __init__(self, raise_error: bool, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.raise_error = raise_error

    async def __call__(self, request: Request) -> str | None:
        api_key = request.headers.get(self.model.name)
        if not api_key:
            if not self.raise_error:
                return None
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization credentials",
            )

        try:
            token_prefix, token = api_key.split(" ")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token schema",
            )

        if token_prefix.lower() != "token":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token schema",
            )

        return token


bearer = HTTPTokenHeader(raise_error=True, name="Authorization")
bearer_optional = HTTPTokenHeader(raise_error=False, name="Authorization")

Token = Annotated[str, Depends(bearer)]
TokenOptional = Annotated[Optional[str], Depends(bearer_optional)]


async def get_current_user(
    session: SessionDB,
    token: Token,
) -> User:
    try:
        payload = jwt.decode(
            token=token,
            key=SETTINGS.SECRET_KEY,
            algorithms=[SETTINGS.ALGORITHM],
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError) as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or expired token.",
        ) from ex
    user_db = await session.get(User, token_data.sub)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found user.",
        )
    return user_db


async def get_current_user_optional(
    session: SessionDB,
    token: TokenOptional,
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(
            token=token,
            key=SETTINGS.SECRET_KEY,
            algorithms=[SETTINGS.ALGORITHM],
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        return None
    user_db = await session.get(User, token_data.sub)
    return user_db


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]
CurrentOptionalUser = Annotated[
    Optional[User],
    Depends(get_current_user_optional),
]
