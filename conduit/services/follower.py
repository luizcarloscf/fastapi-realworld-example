from sqlmodel import delete
from sqlmodel.ext.asyncio.session import AsyncSession
from conduit.models import Follower


async def follow_user(
    *,
    session: AsyncSession,
    follower_id: int,
    followed_id: int,
) -> None:
    session.add(
        Follower(
            follower_id=follower_id,
            following_id=followed_id,
        ),
    )
    await session.commit()


async def unfollow_user(
    *,
    session: AsyncSession,
    follower_id: int,
    followed_id: int,
) -> None:
    query = delete(Follower).where(
        (Follower.follower_id == follower_id)
        & (Follower.following_id == followed_id),
    )
    await session.exec(query)
    await session.commit()
