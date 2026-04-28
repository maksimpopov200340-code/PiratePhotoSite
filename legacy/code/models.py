from typing import Annotated, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
from datetime import datetime
from sqlalchemy import func

class UserBase(SQLModel, table=True):
    __tablename__ = "USERS"
    id: Optional[int] = Field(default=None, primary_key=True)   #Mapped[int] = mapped_column(primary_key=True)
    name: str            #Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    password: str #Mapped[str] = mapped_column(Text, nullable=False)
    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}  # 👈 БД сама заполнит
    )
    posts: List["PostBase"] = Relationship(back_populates="author")
    comments: List["CommentBase"] = Relationship(back_populates="author")

class PostBase(SQLModel, table=True):
    __tablename__ = "POSTS"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=40)
    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}  # 👈 БД сама заполнит
    )
    description: str
    user_id: int=Field(foreign_key="USERS.id", nullable=False)

    #Realation
    author: Optional[UserBase]= Relationship(back_populates="posts")
    comments: List["CommentBase"] = Relationship(back_populates="post")
    images: List["PostImage"] = Relationship(back_populates="post")

class PostImage(SQLModel, table=True):
    __tablename__ = "POST_IMAGES"

    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="POSTS.id", nullable=False)

    bucket_name: str = Field(max_length=100)
    object_name: str = Field(max_length=500, unique=True)
    original_filename: str = Field(max_length=255)
    content_type: str = Field(max_length=100)
    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}
    )

    post: Optional["PostBase"] = Relationship(back_populates="images")
    

class CommentBase(SQLModel, table=True):
    __tablename__ = "COMMENTS"
    id: Optional[int] = Field(default=None, primary_key=True)
    desc_com: str = Field(max_length=50)
    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}  # 👈 БД сама заполнит
    )
    user_id: int=Field(foreign_key="USERS.id", nullable=False)
    post_id: int=Field(foreign_key="POSTS.id", nullable=False)

    #Relation
    author: Optional[UserBase]= Relationship(back_populates="comments")
    post: Optional[PostBase]= Relationship(back_populates="comments")



