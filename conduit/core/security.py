from typing import Any

from fastapi.security import APIKeyHeader
from starlette.requests import Request

from conduit.exceptions import TokenInvalidException, TokenMissingException


class HTTPTokenHeader(APIKeyHeader):
    def __init__(self, raise_error: bool, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.raise_error = raise_error

    async def __call__(self, request: Request) -> str | None:
        api_key = request.headers.get(self.model.name)
        if not api_key:
            if not self.raise_error:
                return None
            raise TokenMissingException()

        try:
            token_prefix, token = api_key.split(" ")
        except ValueError as ex:
            raise TokenInvalidException() from ex

        if token_prefix.lower() != "token":
            raise TokenInvalidException()

        return token
