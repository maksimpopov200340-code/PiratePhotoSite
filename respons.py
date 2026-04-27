from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel


class UserPublic(SQLModel):
    id: int
    name: str


class PostImagePublic(SQLModel):
    id: int
    original_filename: str
    content_type: str
    url: str


class PostPublic(SQLModel):
    id: int
    title: str
    description: str
    created_at: datetime
    user_id: int
    author: Optional[UserPublic] = None
    images: List[PostImagePublic] = []


class PostListItem(SQLModel):
    id: int
    title: str
    description: str
    created_at: datetime
    user_id: int
    image_preview: Optional[str] = None