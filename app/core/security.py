from datetime import datetime, timedelta
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.core.config import SETTINGS

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return PWD_CONTEXT.hash(password)


def create_access_token(subject: str | Any) -> str:
    access_token_expires = timedelta(
        minutes=SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    expire = datetime.utcnow() + access_token_expires
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        claims=to_encode,
        key=SETTINGS.SECRET_KEY,
        algorithm=SETTINGS.ALGORITHM,
    )
    return encoded_jwt
