from typing import List, Optional
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Table, PrimaryKeyConstraint, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime

from conduit.core.database import Base


followers_table = Table(
    "followers",
    Base.metadata,
    Column("follower_id", ForeignKey("users.id"), nullable=False),
    Column("following_id", ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime, nullable=False),
    PrimaryKeyConstraint("following_id", "follower_id"),
)


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(index=True)
    image: Mapped[Optional[str]]
    bio: Mapped[Optional[str]]
    hashed_password: Mapped[str]

    follows: Mapped[List["UserModel"]] = relationship(
        secondary=followers_table,
        primaryjoin=lambda: UserModel.id == followers_table.c.follower_id,
        secondaryjoin=lambda: UserModel.id == followers_table.c.following_id,
    )


class ArticleModel(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(nullable=False, unique=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    body: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    author: Mapped["UserModel"] = relationship(foreign_keys=[author_id])
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, onupdate=datetime.utcnow, default=datetime.utcnow
    )


class CommentModel(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    author: Mapped["UserModel"] = relationship(foreign_keys=[author_id])
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id"), unique=True, nullable=False
    )
    body: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, onupdate=datetime.utcnow, default=datetime.utcnow
    )
