import logging

from fastapi import APIRouter, status

import conduit.services.follower as follower_service
import conduit.services.user as user_service
from conduit.api.dependencies import (
    CurrentOptionalUser,
    CurrentUser,
    SessionDB,
)
from conduit.schemas.profile import ProfileData, ProfileResponse
from conduit.exceptions import (
    ProfileNotFollowedException,
    ProfileNotFoundException,
    ProfileAlreadyFollowedException,
    ProfileFollowYourselfException,
    ProfileUnfollowYourselfException,
)

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
    user, following = response if response else (None, False)
    if not user:
        raise ProfileNotFoundException()
    return ProfileResponse(
        profile=ProfileData(
            username=user.username,
            bio=user.bio,
            image=user.image,
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
    user, following = response if response else (None, False)
    if not user:
        raise ProfileNotFoundException()
    if user.id == current_user.id:
        raise ProfileFollowYourselfException()
    if following:
        raise ProfileAlreadyFollowedException()
    await follower_service.follow_user(
        session=session,
        follower_id=current_user.id,
        followed_id=user.id,
    )
    return ProfileResponse(
        profile=ProfileData(
            username=user.username,
            bio=user.bio,
            image=user.image,
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
    user, following = response if response else (None, False)
    if not user:
        raise ProfileNotFoundException()
    if user.id == current_user.id:
        raise ProfileUnfollowYourselfException()
    if not following:
        raise ProfileNotFollowedException()
    await follower_service.unfollow_user(
        session=session,
        follower_id=current_user.id,
        followed_id=user.id,
    )
    return ProfileResponse(
        profile=ProfileData(
            username=user.username,
            bio=user.bio,
            image=user.image,
            following=False,
        )
    )
