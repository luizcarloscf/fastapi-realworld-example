from datetime import datetime

from sqlalchemy import Column, DateTime, func, text
from sqlmodel import Field, SQLModel


class Follower(SQLModel, table=True):  # type: ignore[call-arg]
    follower_id: int = Field(
        foreign_key="user.id",
        primary_key=True,
    )
    following_id: int = Field(
        foreign_key="user.id",
        primary_key=True,
    )
    created_at: datetime | None = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        )
    )


class Favorite(SQLModel, table=True):  # type: ignore[call-arg]
    user_id: int = Field(
        foreign_key="user.id",
        primary_key=True,
    )
    article_id: int = Field(
        foreign_key="article.id",
        primary_key=True,
        ondelete="CASCADE",
    )
    created_at: datetime | None = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        )
    )


class ArticleTag(SQLModel, table=True):  # type: ignore[call-arg]
    article_id: int = Field(
        foreign_key="article.id",
        primary_key=True,
        ondelete="CASCADE",
    )
    tag_id: int = Field(
        foreign_key="tag.id",
        primary_key=True,
        ondelete="CASCADE",
    )
    created_at: datetime | None = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        )
    )


class User(SQLModel, table=True):  # type: ignore[call-arg]
    id: int | None = Field(
        nullable=False,
        unique=True,
        primary_key=True,
    )
    username: str = Field(
        index=True,
        unique=True,
    )
    email: str = Field(
        index=True,
        unique=True,
    )
    image: str | None = Field(default=None)
    bio: str | None = Field(default=None)
    hashed_password: str = Field(
        nullable=False,
    )
    created_at: datetime | None = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        )
    )
    updated_at: datetime | None = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=func.now(),
        )
    )


class Article(SQLModel, table=True):  # type: ignore[call-arg]
    id: int | None = Field(
        nullable=False,
        unique=True,
        primary_key=True,
    )
    slug: str = Field(
        nullable=False,
        unique=True,
    )
    title: str = Field(
        nullable=False,
    )
    description: str = Field(
        nullable=False,
    )
    body: str = Field(
        nullable=False,
    )
    author_id: int = Field(
        foreign_key="user.id",
        nullable=False,
    )
    created_at: datetime | None = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        )
    )
    updated_at: datetime | None = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=func.now(),
        )
    )


class Tag(SQLModel, table=True):  # type: ignore[call-arg]
    id: int | None = Field(
        nullable=False,
        unique=True,
        primary_key=True,
    )
    name: str = Field(
        unique=True,
        nullable=False,
    )


class Comment(SQLModel, table=True):  # type: ignore[call-arg]
    id: int | None = Field(
        nullable=False,
        unique=True,
        primary_key=True,
    )
    author_id: int = Field(
        foreign_key="user.id",
        nullable=False,
    )
    article_id: int = Field(
        foreign_key="article.id",
        nullable=False,
        ondelete="CASCADE",
    )
    body: str = Field(
        nullable=False,
    )
    created_at: datetime | None = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        )
    )
    updated_at: datetime | None = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=func.now(),
        )
    )
