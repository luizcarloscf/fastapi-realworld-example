from sqlalchemy.orm import Session

from app.models import UserModel
from app.schemas import NewUserRequest, User, UpdateUserRequest
from app.core.security import get_password_hash, verify_password


def get_user_by_id(*, session: Session, user_id: int):
    return session.query(UserModel).filter(UserModel.id == user_id).first()


def get_user_by_email(*, session: Session, email: str):
    return session.query(UserModel).filter(UserModel.email == email).first()


def get_users(*, session: Session, skip: int = 0, limit: int = 100):
    return session.query(UserModel).offset(skip).limit(limit).all()


def create_user(*, session: Session, user: NewUserRequest):
    db_user = UserModel(
        name=user.name,
        email=user.email,
        hashed_password=get_password_hash(user.password.get_secret_value()),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_user(*, session: Session, update: UpdateUserRequest, model: UserModel):
    for var, value in update.model_dump().items():
        if var == "hashed_password":
            value = get_password_hash(update.password.get_secret_value())
        print(value)
        print(var)
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
