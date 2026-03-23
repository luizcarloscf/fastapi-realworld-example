from typing import Dict, List
from unittest import result

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class BaseException(Exception):
    status_code: int
    detail: str
    errors: Dict[str, List[str]] = {}


class UserNotFoundException(BaseException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "User not found"
    errors = {"user": ["not found"]}


class UserNameExistsException(BaseException):
    status_code = status.HTTP_409_CONFLICT
    detail = "User with this username already exists"
    errors = {"username": ["has already been taken"]}


class UserEmailExistsException(BaseException):
    status_code = status.HTTP_409_CONFLICT
    detail = "User with this email already exists"
    errors = {"email": ["has already been taken"]}


class ArticleNotFoundException(BaseException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Article not found"
    errors = {"article": ["not found"]}


class ArticleNotAuthorException(BaseException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Not authorized to modify this article"
    errors = {"article": ["forbidden"]}


class ArticleAlreadyFavoritedException(BaseException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Article already favorited"


class ArticleNotFavoritedException(BaseException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Article not favorited"


class CommentNotFoundException(BaseException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Comment not found"
    errors = {"comment": ["not found"]}


class CommentNotAuthorException(BaseException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Not authorized to delete this comment"
    errors = {"comment": ["forbidden"]}


class ProfileNotFoundException(BaseException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Profile not found"
    errors = {"profile": ["not found"]}


class ProfileAlreadyFollowedException(BaseException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Profile already followed"


class ProfileFollowYourselfException(BaseException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Cannot follow yourself"


class ProfileUnfollowYourselfException(BaseException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Cannot unfollow yourself"


class ProfileNotFollowedException(BaseException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Profile not followed"


class InvalidCredentialsException(BaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid email or password"
    errors = {
        "email": ["incorrect email or password."],
        "password": ["incorrect email or password."],
        "credentials": ["invalid"],
    }


class TokenExpiredException(BaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token has expired"
    errors = {"token": ["expired"]}


class TokenMissingException(BaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token is missing"
    errors = {"token": ["is missing"]}


class TokenInvalidException(BaseException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid token"
    errors = {"token": ["invalid"]}


def add_http_exception_handler(app: FastAPI) -> None:

    @app.exception_handler(BaseException)
    async def _exception_handler(
        _: Request,
        exc: BaseException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "status_code": exc.status_code,
                "message": exc.detail,
                "errors": exc.errors,
            },
        )

    @app.exception_handler(HTTPException)
    async def _http_exception_handler(
        _: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "status_code": exc.status_code,
                "message": exc.detail,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def _request_validation_exception_handler(
        _: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        result: Dict[str, List[str]] = {}
        for error in exc.errors():
            field = error["loc"][-1]
            message = error["msg"]
            if result.get(field) is None:
                result[field] = []
            result[field].append(message.lower().split(", ")[-1])
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "error",
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "Schema validation error",
                "errors": result,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred. Please try again later.",
            },
        )
