from sqlmodel import create_engine, Session, SQLModel
from typing import Annotated
from fastapi import Depends

from models import UserBase, PostBase, CommentBase  # или import models


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    """Создает все таблицы на основе импортированных моделей"""
    from .models import UserBase, PostBase, CommentBase  # явно импортируем
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]