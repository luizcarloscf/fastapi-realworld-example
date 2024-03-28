import logging

from fastapi import APIRouter, Body, HTTPException

import app.api.crud.user as crud
from app.api.deps import SessionDep, TokenDep, CurrentUser
from app.core.security import create_access_token
from app.schemas import (
    NewUserRequest,
    User,
    UserResponse,
    LoginUserRequest,
    UpdateUserRequest,
)

router = APIRouter()
log = logging.getLogger(__name__)


@router.post(
    "/users",
    tags=["users"],
    response_model=UserResponse,
    summary="Register new user",
)
async def add_user(
    session: SessionDep,
    user: NewUserRequest = Body(..., embed=True),
) -> UserResponse:
    log.info("Started POST /users")
    maybe_user = crud.get_user_by_email(session=session, email=user.email)
    if maybe_user:
        raise HTTPException(
            status_code=400,
            detail="User with email already registered",
        )
    instance = crud.create_user(session=session, user=user)
    token = create_access_token(subject=instance.id)
    return UserResponse(
        user=User(
            token=token,
            **user.model_dump(),
        ),
    )


@router.post(
    "/users/login",
    tags=["users"],
    response_model=UserResponse,
    summary="Login with email/password",
)
async def login_user(
    session: SessionDep,
    user: LoginUserRequest = Body(..., embed=True, alias="user"),
) -> UserResponse:
    log.info("Started POST /users/login")
    instance = crud.authenticate(
        session=session,
        email=user.email,
        password=user.password.get_secret_value(),
    )
    if not instance:
        raise HTTPException(
            status_code=400,
            detail="Could not login",
        )
    token = create_access_token(subject=instance.id)
    return UserResponse(
        user=User(
            name=instance.name,
            email=instance.email,
            image=instance.image,
            bio=instance.bio,
            token=token,
        )
    )


@router.get(
    "/user",
    tags=["users"],
    response_model=UserResponse,
    summary="Get current logged user",
)
async def get_user(
    token: TokenDep,
    current_user: CurrentUser,
) -> UserResponse:
    return UserResponse(
        user=User(
            name=current_user.name,
            email=current_user.email,
            image=current_user.image,
            bio=current_user.bio,
            token=token,
        ),
    )


@router.put(
    "/user",
    tags=["users"],
    response_model=UserResponse,
    summary="Update current logged user",
)
async def update_current_user(
    session: SessionDep,
    current_user: CurrentUser,
    token: TokenDep,
    user: UpdateUserRequest = Body(..., embed=True),
) -> UserResponse:
    if user.email:
        existing_user = crud.get_user_by_email(session=session, email=user.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    current_user = crud.update_user(session=session, update=user, model=current_user)
    return UserResponse(
        user=User(
            name=current_user.name,
            email=current_user.email,
            image=current_user.image,
            bio=current_user.bio,
            token=token,
        ),
    )
