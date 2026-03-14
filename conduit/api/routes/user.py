import logging
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException

from conduit.crud import user as user_crud
from conduit.api.deps import CurrentUser, SessionDB, Token
from conduit.core.security import create_access_token

from conduit.schemas.user import (
    UserRegistrationRequest,
    UserResponse,
    UserData,
    UserLogin,
    UserLoginRequest,
    UserUpdateRequest,
)
from conduit.models import User
from conduit.core.security import get_password_hash, verify_password


router = APIRouter()
log = logging.getLogger("conduit.api.users")


@router.post(
    path="/users",
    tags=["users"],
    response_model=UserResponse,
    summary="Register new user",
)
async def add_user(
    session: SessionDB,
    user_request: UserRegistrationRequest,
) -> UserResponse:
    maybe_user = await user_crud.get_user_by_email_or_username(
        session=session,
        email=user_request.user.email,
        username=user_request.user.username,
    )
    if maybe_user:
        raise HTTPException(
            status_code=409,
            detail="User with this email or username already exists.",
        )

    db_user = await user_crud.create_user(
        session=session,
        user_registration=user_request.user,
    )
    return UserResponse(
        user=UserData(
            username=db_user.username,
            email=db_user.email,
            bio=db_user.bio,
            image=db_user.image,
            token=create_access_token(
                subject=db_user.id,
            ),
        )
    )


@router.post(
    path="/users/login",
    tags=["users"],
    response_model=UserResponse,
    summary="Login with email/password",
)
async def login_user(
    session: SessionDB,
    user_request: UserLoginRequest,
) -> UserResponse:
    user_db = await user_crud.authenticate(
        session=session,
        email=user_request.user.email,
        password=user_request.user.password.get_secret_value(),
    )
    if not user_db:
        raise HTTPException(
            status_code=401,
            detail="Invalid password or e-mail, could not login.",
        )

    return UserResponse(
        user=UserData(
            username=user_db.username,
            email=user_db.email,
            bio=user_db.bio,
            image=user_db.image,
            token=create_access_token(subject=user_db.id),
        ),
    )


@router.get(
    path="/user",
    tags=["users"],
    response_model=UserResponse,
    summary="Get current logged user",
)
async def get_user(
    token: Token,
    current_user: CurrentUser,
) -> UserResponse:
    return UserResponse(
        user=UserData(
            username=current_user.username,
            email=current_user.email,
            bio=current_user.bio,
            image=current_user.image,
            token=token,
        )
    )


@router.put(
    path="/user",
    tags=["users"],
    response_model=UserResponse,
    summary="Update current logged user",
)
async def update_current_user(
    session: SessionDB,
    current_user: CurrentUser,
    token: Token,
    user_update_request: UserUpdateRequest,
) -> UserResponse:
    if user_update_request.user.email:
        existing_user = await user_crud.get_user_by_email(
            session=session,
            email=user_update_request.user.email,
        )
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409,
                detail="User with this email already exists.",
            )

    if user_update_request.user.username:
        existing_user = await user_crud.get_user_by_username(
            session=session,
            username=user_update_request.user.username,
        )
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409,
                detail="User with this username already exists.",
            )

    current_user = await user_crud.update_user(
        session=session,
        user_update=user_update_request.user,
        user_current=current_user,
    )
    return UserResponse(
        user=UserData(
            email=current_user.email,
            username=current_user.username,
            bio=current_user.bio,
            image=current_user.image,
            token=token,
        ),
    )
