import logging

from fastapi import APIRouter, status

import conduit.services.follower as follower_service
import conduit.services.user as user_service
from conduit.api.dependencies import CurrentOptionalUser, CurrentUser, SessionDB
from conduit.exceptions import (
    ProfileAlreadyFollowedException,
    ProfileFollowYourselfException,
    ProfileNotFollowedException,
    ProfileNotFoundException,
    ProfileUnfollowYourselfException,
)
from conduit.schemas.profile import ProfileData, ProfileResponse

router = APIRouter()
log = logging.getLogger("conduit.api.profiles")


@router.get(
    path="/profiles/{username}",
    tags=["profiles"],
    response_model=ProfileResponse,
    summary="Get a user profile.",
    status_code=status.HTTP_200_OK,
)
async def get_profile(
    username: str,
    session: SessionDB,
    current_user: CurrentOptionalUser,
) -> ProfileResponse:
    response = await user_service.get_user_by_username(
        session=session,
        username=username,
        current_user_id=current_user.id if current_user else None,
    )
    user_db, following = response if response else (None, False)
    if not user_db:
        raise ProfileNotFoundException()
    return ProfileResponse(
        profile=ProfileData(
            username=user_db.username,
            bio=user_db.bio,
            image=user_db.image,
            following=following,
        )
    )


@router.post(
    path="/profiles/{username}/follow",
    tags=["profiles"],
    response_model=ProfileResponse,
    summary="Follow a user.",
    status_code=status.HTTP_200_OK,
)
async def follow_user(
    username: str,
    session: SessionDB,
    current_user: CurrentUser,
) -> ProfileResponse:
    response = await user_service.get_user_by_username(
        session=session,
        username=username,
        current_user_id=current_user.id,
    )
    user_db, following = response if response else (None, False)
    if not user_db:
        raise ProfileNotFoundException()
    if user_db.id == current_user.id:
        raise ProfileFollowYourselfException()
    if following:
        raise ProfileAlreadyFollowedException()
    await follower_service.follow_user(
        session=session,
        follower_id=current_user.id,  # type: ignore[arg-type]
        followed_id=user_db.id,  # type: ignore[arg-type]
    )
    return ProfileResponse(
        profile=ProfileData(
            username=user_db.username,
            bio=user_db.bio,
            image=user_db.image,
            following=True,
        )
    )


@router.delete(
    path="/profiles/{username}/follow",
    tags=["profiles"],
    response_model=ProfileResponse,
    summary="Unfollow a user.",
    status_code=status.HTTP_200_OK,
)
async def unfollow_user(
    username: str,
    session: SessionDB,
    current_user: CurrentUser,
) -> ProfileResponse:
    response = await user_service.get_user_by_username(
        session=session,
        username=username,
        current_user_id=current_user.id,
    )
    user_db, following = response if response else (None, False)
    if not user_db:
        raise ProfileNotFoundException()
    if user_db.id == current_user.id:
        raise ProfileUnfollowYourselfException()
    if not following:
        raise ProfileNotFollowedException()
    await follower_service.unfollow_user(
        session=session,
        follower_id=current_user.id,  # type: ignore[arg-type]
        followed_id=user_db.id,  # type: ignore[arg-type]
    )
    return ProfileResponse(
        profile=ProfileData(
            username=user_db.username,
            bio=user_db.bio,
            image=user_db.image,
            following=False,
        )
    )
