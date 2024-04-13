from typing import Optional

from sqlalchemy.orm import Session
from slugify import slugify

from conduit.core.security import get_password_hash, verify_password
from conduit.models import UserModel, ArticleModel, CommentModel
from conduit.schemas.users import NewUserRequest, UpdateUserRequest
from conduit.schemas.articles import NewArticleRequest


def get_user_by_id(*, session: Session, user_id: int):
    return session.query(UserModel).filter(UserModel.id == user_id).first()


def get_user_by_email(*, session: Session, email: str):
    return session.query(UserModel).filter(UserModel.email == email).first()


def create_user(*, session: Session, request: NewUserRequest):
    db_user = UserModel(
        username=request.username,
        email=request.email,
        hashed_password=get_password_hash(request.password.get_secret_value()),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_user(*, session: Session, request: UpdateUserRequest, user: UserModel):
    for var, value in request.model_dump().items():
        if var == "password" and value is not None:
            value = get_password_hash(request.password.get_secret_value())
            setattr(user, "hashed_password", value)
            continue
        setattr(user, var, value) if value else None
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate(*, session: Session, email: str, password: str):
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def get_article_by_slug(
    *,
    session: Session,
    slug: str,
) -> Optional[ArticleModel]:
    return session.query(ArticleModel).filter(ArticleModel.slug == slug).first()


def create_article(
    *,
    session: Session,
    request: NewArticleRequest,
    user: UserModel,
) -> ArticleModel:
    instance = ArticleModel(
        author=user,
        title=request.title,
        description=request.description,
        body=request.body,
        slug=slugify(request.title),
    )
    session.add(instance)
    session.commit()
    session.refresh(instance)
    return instance
