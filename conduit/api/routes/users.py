import logging
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException
from opentelemetry import trace

from conduit import crud
from conduit.api.deps import CurrentUserDep, SessionDep, TokenDep
from conduit.core.security import create_access_token
from conduit.schemas.users import (
    LoginUserRequest,
    NewUserRequest,
    UpdateUserRequest,
    User,
    UserResponse,
    UserModelView,
)

router = APIRouter()
log = logging.getLogger("conduit.api.users")
log.setLevel(level=logging.DEBUG)
tracer = trace.get_tracer(__name__)


@router.post(
    path="/users",
    tags=["users"],
    response_model=UserResponse,
    summary="Register new user",
)
@tracer.start_as_current_span(name="POST /users add_user")
async def add_user(
    session: SessionDep,
    user: Annotated[NewUserRequest, Body(embed=True)],
) -> UserResponse:
    log.info("Start POST /user add_user")
    maybe_user = crud.get_user_by_email(session=session, email=user.email)
    if maybe_user:
        msg = "User with email already registered."
        log.error(msg=msg)
        raise HTTPException(status_code=400, detail="msg")
    instance = crud.create_user(session=session, request=user)
    instance_view = UserModelView.model_validate(instance)
    token = create_access_token(subject=instance_view.id)
    return UserResponse(user=User(token=token, **instance_view.model_dump()))


@router.post(
    path="/users/login",
    tags=["users"],
    response_model=UserResponse,
    summary="Login with email/password",
)
@tracer.start_as_current_span(name="POST /users/login login_user")
async def login_user(
    session: SessionDep,
    user: Annotated[LoginUserRequest, Body(embed=True)],
) -> UserResponse:
    log.info("Started POST /users/login")
    instance = crud.authenticate(
        session=session,
        email=user.email,
        password=user.password.get_secret_value(),
    )
    if not instance:
        msg = "Invalid password, could not login."
        log.error(msg=msg)
        raise HTTPException(status_code=400, detail=msg)
    token = create_access_token(subject=instance.id)
    instance_view = UserModelView.model_validate(instance)
    return UserResponse(user=User(**instance_view.model_dump(), token=token))


@router.get(
    path="/user",
    tags=["users"],
    response_model=UserResponse,
    summary="Get current logged user",
)
@tracer.start_as_current_span(name="GET /user get_user")
async def get_user(
    token: TokenDep,
    current_user: CurrentUserDep,
) -> UserResponse:
    log.info("Start GET /user get_user")
    instance_view = UserModelView.model_validate(current_user)
    return UserResponse(user=User(**instance_view.model_dump(), token=token))


@router.put(
    path="/user",
    tags=["users"],
    response_model=UserResponse,
    summary="Update current logged user",
)
@tracer.start_as_current_span(name="PUT /users update_current_user")
async def update_current_user(
    session: SessionDep,
    current_user: CurrentUserDep,
    token: TokenDep,
    user: Annotated[UpdateUserRequest, Body(embed=True)],
) -> UserResponse:
    log.info("Start PUT /user update_user")
    if user.email:
        existing_user = crud.get_user_by_email(session=session, email=user.email)
        if existing_user and existing_user.id != current_user.id:
            msg = "User with this email already exists."
            log.error(msg=msg)
            raise HTTPException(status_code=409, detail=msg)
    current_user = crud.update_user(session=session, request=user, user=current_user)
    instance_view = UserModelView.model_validate(current_user)
    return UserResponse(user=User(**instance_view.model_dump(), token=token))
