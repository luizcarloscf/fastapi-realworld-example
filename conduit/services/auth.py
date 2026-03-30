from datetime import datetime, timedelta, timezone

from jose import jwt


def create_access_token(
    *,
    subject: str,
    expires_minutes: int,
    secret_key: str,
    algorithm: str,
) -> str:
    access_token_expires = timedelta(
        minutes=expires_minutes,
    )
    expire = datetime.now(timezone.utc) + access_token_expires
    to_encode = {
        "exp": expire,
        "sub": str(subject),
    }
    encoded_jwt = jwt.encode(
        claims=to_encode,
        key=secret_key,
        algorithm=algorithm,
    )
    return encoded_jwt
