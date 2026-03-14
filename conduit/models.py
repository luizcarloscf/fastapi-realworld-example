from typing import List
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel, Relationship


def _utcnow():
    return datetime.now(timezone.utc).replace(microsecond=0)


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
    id: int | None = Field(nullable=False, unique=True, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    image: str | None = Field(default=None)
    bio: str | None = Field(default=None)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(nullable=False, default_factory=_utcnow)
    updated_at: datetime = Field(nullable=False, default_factory=_utcnow)

    # articles: List["Article"] = Relationship(back_populates="author")
    # comments: List["Comment"] = Relationship(back_populates="author")
    # favorites: List["Article"] = Relationship(back_populates="favorited_by", link_model=Favorite)
    # following: List["User"] = Relationship(
    #     back_populates="followers",
    #     link_model=Follower,
    #     sa_relationship_kwargs={
    #         "primaryjoin": "User.id==Follower.follower_id",
    #         "secondaryjoin": "User.id==Follower.following_id",
    #     },
    # )
    # followers: List["User"] = Relationship(
    #     back_populates="following",
    #     link_model=Follower,
    #     sa_relationship_kwargs={
    #         "primaryjoin": "User.id==Follower.following_id",
    #         "secondaryjoin": "User.id==Follower.follower_id",
    #     },
    # )


class Article(SQLModel, table=True):
    id: int | None = Field(nullable=False, unique=True, primary_key=True)
    slug: str = Field(nullable=False, unique=True)
    title: str = Field(nullable=False)
    description: str = Field(nullable=False)
    body: str = Field(nullable=False)
    author_id: int = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(nullable=False, default_factory=_utcnow)
    updated_at: datetime = Field(nullable=False, default_factory=_utcnow)

    # author: "User" = Relationship(back_populates="articles")
    # tags: List["Tag"] = Relationship(back_populates="articles", link_model=ArticleTag)
    # favorited_by: List["User"] = Relationship(back_populates="favorites", link_model=Favorite)
    # comments: List["Comment"] = Relationship(back_populates="article")


class Tag(SQLModel, table=True):
    id: int | None = Field(nullable=False, unique=True, primary_key=True)
    name: str = Field(unique=True, nullable=False)

    # articles: List["Article"] = Relationship(back_populates="tags", link_model=ArticleTag)


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
    updated_at: datetime = Field(nullable=False, default_factory=_utcnow)

    # author: "User" = Relationship(back_populates="comments")
    # article: "Article" = Relationship(back_populates="comments")
