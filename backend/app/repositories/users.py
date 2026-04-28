from fastapi import HTTPException
from sqlmodel import Session, select

from ..models import User
from ..schemas import UserCreate


def list_users(session: Session) -> list[User]:
    statement = select(User).order_by(User.id)
    return list(session.exec(statement))


def get_user_or_404(session: Session, user_id: int) -> User:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return user


def create_user(session: Session, payload: UserCreate) -> User:
    username = payload.username.strip()
    password = payload.password.strip()

    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty.")

    if not password:
        raise HTTPException(status_code=400, detail="Password cannot be empty.")

    statement = select(User).where(User.username == username)
    existing_user = session.exec(statement).first()
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Username already exists.")

    user = User(username=username, password=password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
