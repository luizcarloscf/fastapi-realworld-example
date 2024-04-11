from typing import List, Optional

from sqlalchemy import Column, Integer, Unicode, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime

from conduit.core.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(index=True)
    image: Mapped[Optional[str]]
    bio: Mapped[Optional[str]]
    hashed_password: Mapped[str]


class ArticleModel(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(nullable=False, unique=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    body: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    author: Mapped["UserModel"] = relationship(foreign_keys=[author_id])


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
