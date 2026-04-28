from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class UserCreate(SQLModel):
    username: str
    password: str


class UserRead(SQLModel):
    id: int
    username: str
    created_at: datetime


class CommentCreate(SQLModel):
    user_id: int
    text: str


class CommentRead(SQLModel):
    id: int
    text: str
    created_at: datetime
    author: UserRead


class PostListItem(SQLModel):
    id: int
    text: str
    created_at: datetime
    author: UserRead
    image_url: Optional[str] = None
    comment_count: int


class PostRead(SQLModel):
    id: int
    text: str
    created_at: datetime
    author: UserRead
    image_url: Optional[str] = None
    comments: list[CommentRead] = Field(default_factory=list)
