from typing import Optional, Tuple


from sqlmodel import select, exists
from sqlmodel.ext.asyncio.session import AsyncSession

from conduit.services.password import get_password_hash, verify_password
from conduit.models import User, Follower
from conduit.schemas.user import UserRegistration, UserUpdate


async def get_user_by_id(
    *,
    session: AsyncSession,
    user_id: int,
) -> Optional[User]:
    query = select(User).where(
        User.id == user_id,
    )
    result = await session.exec(query)
    return result.one_or_none()


async def get_user_by_email(
    *,
    session: AsyncSession,
    email: str,
) -> Optional[User]:
    query = select(User).where(
        User.email == email,
    )
    result = await session.exec(query)
    return result.one_or_none()


async def get_user_by_username(
    *,
    session: AsyncSession,
    username: str,
    current_user_id: int = 0,
) -> Optional[Tuple[User, bool]]:
    query = select(
        User,
        exists()
        .where(
            (Follower.follower_id == current_user_id)
            & (Follower.following_id == User.id)
        )
        .label("following"),
    ).where(
        User.username == username,
    )
    result = await session.exec(query)
    return result.one_or_none()


async def create_user(
    *,
    session: AsyncSession,
    user_registration: UserRegistration,
) -> User:
    user_data = user_registration.model_dump(exclude_unset=True)
    user_data["hashed_password"] = get_password_hash(
        password=user_data["password"].get_secret_value(),
    )
    del user_data["password"]
    user_db = User(**user_data)
    session.add(user_db)
    await session.commit()
    await session.refresh(user_db)
    return user_db


async def update_user(
    *,
    session: AsyncSession,
    user_update: UserUpdate,
    user_current: User,
) -> User:
    user_data = user_update.model_dump(exclude_unset=True)
    if "password" in user_data:
        user_data["hashed_password"] = get_password_hash(
            password=user_data["password"].get_secret_value(),
        )
        del user_data["password"]

    user_current.sqlmodel_update(user_data)
    session.add(user_current)
    await session.commit()
    await session.refresh(user_current)
    return user_current
