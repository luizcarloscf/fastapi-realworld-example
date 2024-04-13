from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.openapi.models import HTTPBearer as HTTPBearerModel
from fastapi.security.http import HTTPBase
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from pydantic import ValidationError
from starlette.requests import Request

from conduit import crud
from conduit.core.config import SETTINGS
from conduit.core.database import SessionLocal, get_db
from conduit.models import UserModel
from conduit.schemas.token import TokenPayload


class HTTPToken(HTTPBase):

    def __init__(
        self,
        *,
        bearerFormat: Optional[str] = None,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        self.model = HTTPBearerModel(bearerFormat=bearerFormat, description=description)
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        if scheme.lower() != "token":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication credentials",
                )
            else:
                return None
        return credentials


bearer = HTTPToken(auto_error=True)

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
            detail="Invalid credentials or expired token.",
        ) from ex
    instance = crud.get_user_by_id(session=session, user_id=token_data.sub)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found user.",
        )
    return instance


CurrentUserDep = Annotated[UserModel, Depends(get_current_user)]
