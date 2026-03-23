import logging

from fastapi import APIRouter, status

from conduit.services import user as user_service
from conduit.services import password as password_service
from conduit.api.dependencies import (
    CurrentUser,
    SessionDB,
    SettingsDep,
    Token,
)
from conduit.services.auth import create_access_token

from conduit.schemas.user import (
    UserRegistrationRequest,
    UserResponse,
    UserData,
    UserLoginRequest,
    UserUpdateRequest,
)
from conduit.exceptions import (
    UserEmailExistsException,
    InvalidCredentialsException,
    UserNameExistsException,
    UserNotFoundException,
)

router = APIRouter()
log = logging.getLogger("conduit.api.users")


@router.post(
    path="/users",
    tags=["users"],
    response_model=UserResponse,
    summary="Register new user",
    status_code=status.HTTP_201_CREATED,
)
async def add_user(
    session: SessionDB,
    user_request: UserRegistrationRequest,
    settings: SettingsDep,
) -> UserResponse:
    user = user_request.user
    maybe_user = await user_service.get_user_by_email(
        session=session,
        email=user.email,
    )
    if maybe_user:
        raise UserEmailExistsException()

    maybe_user = await user_service.get_user_by_username(
        session=session,
        username=user.username,
    )
    if maybe_user:
        raise UserNameExistsException()

    db_user = await user_service.create_user(
        session=session,
        user_registration=user,
    )
    return UserResponse(
        user=UserData(
            username=db_user.username,
            email=db_user.email,
            bio=db_user.bio,
            image=db_user.image,
            token=create_access_token(
                subject=db_user.id,
                expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                secret_key=settings.SECRET_KEY,
                algorithm=settings.ALGORITHM,
            ),
        )
    )


@router.post(
    path="/users/login",
    tags=["users"],
    response_model=UserResponse,
    summary="Login with email/password",
    status_code=status.HTTP_200_OK,
)
async def login_user(
    session: SessionDB,
    user_request: UserLoginRequest,
    settings: SettingsDep,
) -> UserResponse:
    user = user_request.user
    user_db = await user_service.get_user_by_email(
        session=session,
        email=user.email,
    )
    if not user_db:
        raise UserNotFoundException()
    if not password_service.verify_password(
        plain_password=user.password.get_secret_value(),
        hashed_password=user_db.hashed_password,
    ):
        raise InvalidCredentialsException()

    return UserResponse(
        user=UserData(
            username=user_db.username,
            email=user_db.email,
            bio=user_db.bio,
            image=user_db.image,
            token=create_access_token(
                subject=user_db.id,
                expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                secret_key=settings.SECRET_KEY,
                algorithm=settings.ALGORITHM,
            ),
        ),
    )


@router.get(
    path="/user",
    tags=["users"],
    response_model=UserResponse,
    summary="Get current logged user",
    status_code=status.HTTP_200_OK,
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
    status_code=status.HTTP_200_OK,
)
async def update_current_user(
    session: SessionDB,
    current_user: CurrentUser,
    token: Token,
    user_request: UserUpdateRequest,
) -> UserResponse:
    user = user_request.user
    if user.email:
        existing_user = await user_service.get_user_by_email(
            session=session,
            email=user.email,
        )
        if existing_user and existing_user.id != current_user.id:
            raise UserEmailExistsException()

    if user.username:
        response = await user_service.get_user_by_username(
            session=session,
            username=user.username,
            current_user_id=current_user.id,
        )
        existing_user = response[0] if response else None
        if existing_user and existing_user.id != current_user.id:
            raise UserNameExistsException()

    current_user = await user_service.update_user(
        session=session,
        user_update=user,
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
