from collections.abc import Generator
from typing import Annotated, Optional, cast

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import ValidationError
from starlette.requests import Request


from app.core.config import SETTINGS
from app.core.database import SessionLocal, get_db

from app.api.crud.user import get_user_by_id
from app.schemas import TokenPayload
from app.models import UserModel


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            return credentials.credentials
        raise HTTPException(status_code=403, detail="Invalid authorization code.")


bearer = JWTBearer(auto_error=False)

SessionDep = Annotated[SessionLocal, Depends(get_db)]
TokenDep = Annotated[str, Depends(bearer)]


def get_current_user(session: SessionDep, token: TokenDep) -> UserModel:
    try:
        payload = jwt.decode(
            token=token,
            key=SETTINGS.SECRET_KEY,
            algorithms=[SETTINGS.ALGORITHM],
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError) as ex:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from ex
    instance = get_user_by_id(session=session, user_id=token_data.sub)
    if not instance:
        raise HTTPException(status_code=404, detail="User not found")
    return instance


CurrentUser = Annotated[UserModel, Depends(get_current_user)]
