from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _utcnow():
    return datetime.now(timezone.utc)


class Follower(SQLModel, table=True):
    follower_id: int = Field(
        foreign_key="user.id", primary_key=True, ondelete="CASCADE"
    )
    following_id: int = Field(
        foreign_key="user.id", primary_key=True, ondelete="CASCADE"
    )
    created_at: datetime = Field(nullable=False, default_factory=_utcnow)


class Favorite(SQLModel, table=True):
    user_id: int = Field(
        foreign_key="user.id", primary_key=True, ondelete="CASCADE"
    )
    article_id: int = Field(
        foreign_key="article.id", primary_key=True, ondelete="CASCADE"
    )
    created_at: datetime = Field(nullable=False, default_factory=_utcnow)


class ArticleTag(SQLModel, table=True):
    article_id: int = Field(
        foreign_key="article.id", primary_key=True, ondelete="CASCADE"
    )
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)
    created_at: datetime = Field(nullable=False, default_factory=_utcnow)


class User(SQLModel, table=True):
    id: int | None = Field(
        nullable=False,
        unique=True,
        primary_key=True,
        sa_column_kwargs={"autoincrement": True},
    )
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    image: str | None = Field(default=None)
    bio: str | None = Field(default=None)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(nullable=False, default_factory=_utcnow)
    updated_at: datetime = Field(
        nullable=False,
        default_factory=_utcnow,
        sa_column_kwargs={"onupdate": _utcnow},
    )


class Article(SQLModel, table=True):
    id: int | None = Field(nullable=False, unique=True, primary_key=True)
    slug: str = Field(nullable=False, unique=True)
    title: str = Field(nullable=False)
    description: str = Field(nullable=False)
    body: str = Field(nullable=False)
    author_id: int = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(nullable=False, default_factory=_utcnow)
    updated_at: datetime = Field(
        nullable=False,
        default_factory=_utcnow,
        sa_column_kwargs={"onupdate": _utcnow},
    )


class Tag(SQLModel, table=True):
    id: int | None = Field(nullable=False, unique=True, primary_key=True)
    name: str = Field(unique=True, nullable=False)


class Comment(SQLModel, table=True):
    id: int | None = Field(nullable=False, unique=True, primary_key=True)
    author_id: int = Field(
        foreign_key="user.id",
        nullable=False,
        ondelete="CASCADE",
    )
    article_id: int = Field(
        foreign_key="article.id",
        nullable=False,
        ondelete="CASCADE",
    )
    body: str = Field(nullable=False)
    created_at: datetime = Field(nullable=False, default_factory=_utcnow)
    updated_at: datetime = Field(
        nullable=False,
        default_factory=_utcnow,
        sa_column_kwargs={"onupdate": _utcnow},
    )
