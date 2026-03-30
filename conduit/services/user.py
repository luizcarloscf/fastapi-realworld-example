from typing import Tuple

from sqlmodel import exists, select
from sqlmodel.ext.asyncio.session import AsyncSession

from conduit.models import Follower, User
from conduit.schemas.user import UserRegistration, UserUpdate
from conduit.services import password as password_service


async def get_user_by_id(
    *,
    session: AsyncSession,
    user_id: int | None,
) -> User | None:
    if user_id is None:
        return None
    query = select(User).where(
        User.id == user_id,
    )
    result = await session.exec(query)
    return result.one_or_none()


async def get_user_by_email(
    *,
    session: AsyncSession,
    email: str,
) -> User | None:
    query = select(User).where(
        User.email == email,
    )
    result = await session.exec(query)
    return result.one_or_none()


async def get_user_by_username(
    *,
    session: AsyncSession,
    username: str,
    current_user_id: int | None = None,
) -> Tuple[User, bool] | None:
    if current_user_id is None:
        current_user_id = 0
    query = select(
        User,
        exists()
        .where((Follower.follower_id == current_user_id) & (Follower.following_id == User.id))
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
    user_data["hashed_password"] = password_service.get_password_hash(
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
        user_data["hashed_password"] = password_service.get_password_hash(
            password=user_data["password"].get_secret_value(),
        )
        del user_data["password"]

    user_current.sqlmodel_update(user_data)
    session.add(user_current)
    await session.commit()
    await session.refresh(user_current)
    return user_current
