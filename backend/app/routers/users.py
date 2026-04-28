from fastapi import APIRouter

from ..database import SessionDep
from ..presenters import to_user_read
from ..repositories import users as users_repo
from ..schemas import UserCreate, UserRead


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserRead])
def list_users(session: SessionDep) -> list[UserRead]:
    users = users_repo.list_users(session)
    return [to_user_read(user) for user in users]


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: SessionDep) -> UserRead:
    user = users_repo.get_user_or_404(session, user_id)
    return to_user_read(user)


@router.post("/", response_model=UserRead, status_code=201)
def create_user(payload: UserCreate, session: SessionDep) -> UserRead:
    user = users_repo.create_user(session, payload)
    return to_user_read(user)
