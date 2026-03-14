import logging

from fastapi import APIRouter, HTTPException

import conduit.crud.follower as crud_follower
import conduit.crud.user as crud_user
from conduit.api.deps import SessionDB, CurrentUser, CurrentOptionalUser
from conduit.schemas.profile import ProfileData, ProfileResponse

router = APIRouter()


@router.get(
    path="/profiles/{username}",
    tags=["profiles"],
    response_model=ProfileResponse,
    summary="Get a user profile.",
)
async def get_profile(
    username: str,
    session: SessionDB,
    current_user: CurrentOptionalUser,
) -> ProfileResponse:
    user = await crud_user.get_user_by_username(
        session=session,
        username=username,
    )
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Profile not found.",
        )
    if current_user:
        following = await crud_follower.is_following(
            session=session,
            follower=current_user,
            followed=user,
        )
    else:
        following = False
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
)
async def follow_user(
    username: str,
    session: SessionDB,
    current_user: CurrentUser,
) -> ProfileResponse:
    user = await crud_user.get_user_by_username(
        session=session,
        username=username,
    )
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Profile not found.",
        )
    if user.id == current_user.id:
        raise HTTPException(
            status_code=422,
            detail="Cannot follow yourself.",
        )
    await crud_follower.follow_user(
        session=session,
        follower=current_user,
        followed=user,
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
)
async def unfollow_user(
    username: str,
    session: SessionDB,
    current_user: CurrentUser,
) -> ProfileResponse:
    user = await crud_user.get_user_by_username(
        session=session,
        username=username,
    )
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Profile not found.",
        )
    if user.id == current_user.id:
        raise HTTPException(
            status_code=422,
            detail="Cannot unfollow yourself.",
        )
    await crud_follower.unfollow_user(
        session=session,
        follower=current_user,
        followed=user,
    )
    return ProfileResponse(
        profile=ProfileData(
            username=user.username,
            bio=user.bio,
            image=user.image,
            following=False,
        )
    )
