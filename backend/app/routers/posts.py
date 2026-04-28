from typing import Annotated, Optional

from fastapi import APIRouter, File, Form, Query, UploadFile

from ..database import SessionDep
from ..presenters import to_post_list_item, to_post_read
from ..repositories import posts as posts_repo
from ..repositories import users as users_repo
from ..schemas import PostListItem, PostRead
from ..storage import save_post_image


router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=list[PostListItem])
def list_posts(
    session: SessionDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[PostListItem]:
    posts = posts_repo.list_posts(session, offset=offset, limit=limit)
    return [to_post_list_item(post) for post in posts]


@router.get("/{post_id}", response_model=PostRead)
def get_post(post_id: int, session: SessionDep) -> PostRead:
    post = posts_repo.get_post_or_404(session, post_id)
    return to_post_read(post)


@router.post("/", response_model=PostRead, status_code=201)
def create_post(
    session: SessionDep,
    user_id: Annotated[int, Form(...)],
    text: Annotated[str, Form(...)],
    image: Annotated[Optional[UploadFile], File()] = None,
) -> PostRead:
    users_repo.get_user_or_404(session, user_id)
    post = posts_repo.create_post(session, user_id=user_id, text=text)

    saved_image = save_post_image(post.id, image)
    if saved_image is not None:
        file_name, file_path = saved_image
        posts_repo.attach_image(session, post, file_name=file_name, file_path=file_path)

    post = posts_repo.get_post_or_404(session, post.id)
    return to_post_read(post)
