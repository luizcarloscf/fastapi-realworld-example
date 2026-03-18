from typing import Optional

from sqlmodel import select, delete, exists
from sqlmodel.ext.asyncio.session import AsyncSession
from conduit.models import User, Follower


async def is_following(
    session: AsyncSession,
    follower: User,
    followed: User,
) -> bool:
    query = select(
        exists().where(
            (Follower.follower_id == follower.id)
            & (Follower.following_id == followed.id),
        ),
    )
    result = await session.exec(query)
    return result.one()


async def follow_user(
    session: AsyncSession,
    follower: User,
    followed: User,
) -> None:
    if not await is_following(
        session=session,
        follower=follower,
        followed=followed,
    ):
        session.add(
            Follower(
                follower_id=follower.id,
                following_id=followed.id,
            ),
        )
        await session.commit()


async def unfollow_user(
    session: AsyncSession,
    follower: User,
    followed: User,
) -> None:
    query = delete(Follower).where(
        (Follower.follower_id == follower.id)
        & (Follower.following_id == followed.id),
    )
    await session.exec(query)
    await session.commit()
