from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=50)
    password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    posts: List["Post"] = Relationship(back_populates="author")
    comments: List["Comment"] = Relationship(back_populates="author")


class Post(SQLModel, table=True):
    __tablename__ = "posts"

    id: Optional[int] = Field(default=None, primary_key=True)
    text: str = Field(max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    user_id: int = Field(foreign_key="users.id", nullable=False)

    author: Optional["User"] = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post")
    images: List["PostImage"] = Relationship(back_populates="post")


class PostImage(SQLModel, table=True):
    __tablename__ = "post_images"

    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="posts.id", nullable=False)
    file_name: str = Field(max_length=255)
    file_path: str = Field(max_length=500, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    post: Optional["Post"] = Relationship(back_populates="images")


class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: Optional[int] = Field(default=None, primary_key=True)
    text: str = Field(max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    post_id: int = Field(foreign_key="posts.id", nullable=False)

    author: Optional["User"] = Relationship(back_populates="comments")
    post: Optional["Post"] = Relationship(back_populates="comments")
