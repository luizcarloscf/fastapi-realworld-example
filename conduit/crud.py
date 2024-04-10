from sqlalchemy.orm import Session

from conduit.core.security import get_password_hash, verify_password
from conduit.models import UserModel
from conduit.schemas.users import NewUserRequest, UpdateUserRequest


def get_user_by_id(*, session: Session, user_id: int):
    return session.query(UserModel).filter(UserModel.id == user_id).first()


def get_user_by_email(*, session: Session, email: str):
    return session.query(UserModel).filter(UserModel.email == email).first()


def create_user(*, session: Session, user: NewUserRequest):
    db_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password.get_secret_value()),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_user(*, session: Session, update: UpdateUserRequest, model: UserModel):
    for var, value in update.model_dump().items():
        if var == "password" and value is not None:
            value = get_password_hash(update.password.get_secret_value())
            setattr(model, "hashed_password", value)
            continue
        setattr(model, var, value) if value else None
    session.add(model)
    session.commit()
    session.refresh(model)
    return model


def authenticate(*, session: Session, email: str, password: str):
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user
