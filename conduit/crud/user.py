from typing import Optional


from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from conduit.core.security import get_password_hash, verify_password
from conduit.models import User
from conduit.schemas.user import UserRegistration, UserUpdate


async def get_user_by_id(
    session: AsyncSession,
    user_id: int,
) -> Optional[User]:
    return await session.get(User, user_id)


async def get_user_by_email(
    session: AsyncSession,
    email: str,
) -> Optional[User]:
    query = select(User).where(
        User.email == email,
    )
    result = await session.exec(query)
    return result.first()


async def get_user_by_username(
    session: AsyncSession,
    username: str,
) -> Optional[User]:
    query = select(User).where(
        User.username == username,
    )
    result = await session.exec(query)
    return result.first()


async def get_user_by_email_or_username(
    session: AsyncSession,
    email: str,
    username: str,
) -> Optional[User]:
    query = select(User).where(
        (User.email == email) | (User.username == username),
    )
    result = await session.exec(query)
    return result.first()


async def create_user(
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


async def authenticate(
    session: AsyncSession,
    email: str,
    password: str,
) -> Optional[User]:
    db_user = await get_user_by_email(
        session=session,
        email=email,
    )
    if not db_user:
        return None
    if not verify_password(
        plain_password=password,
        hashed_password=db_user.hashed_password,
    ):
        return None
    return db_user
