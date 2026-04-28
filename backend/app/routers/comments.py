from fastapi import APIRouter

from ..database import SessionDep
from ..presenters import to_comment_read
from ..repositories import comments as comments_repo
from ..repositories import posts as posts_repo
from ..repositories import users as users_repo
from ..schemas import CommentCreate, CommentRead


router = APIRouter(prefix="/posts/{post_id}/comments", tags=["comments"])


@router.get("/", response_model=list[CommentRead])
def list_comments(post_id: int, session: SessionDep) -> list[CommentRead]:
    posts_repo.get_post_or_404(session, post_id)
    comments = comments_repo.list_comments_for_post(session, post_id)
    return [to_comment_read(comment) for comment in comments]


@router.post("/", response_model=CommentRead, status_code=201)
def create_comment(
    post_id: int,
    payload: CommentCreate,
    session: SessionDep,
) -> CommentRead:
    posts_repo.get_post_or_404(session, post_id)
    users_repo.get_user_or_404(session, payload.user_id)
    comment = comments_repo.create_comment(
        session,
        post_id=post_id,
        user_id=payload.user_id,
        text=payload.text,
    )
    return to_comment_read(comment)
