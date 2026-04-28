from fastapi import HTTPException
from sqlmodel import Session, select

from ..models import Post, PostImage


def list_posts(session: Session, offset: int, limit: int) -> list[Post]:
    statement = (
        select(Post)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(session.exec(statement))


def get_post_or_404(session: Session, post_id: int) -> Post:
    post = session.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found.")

    return post


def create_post(session: Session, user_id: int, text: str) -> Post:
    cleaned_text = text.strip()
    if not cleaned_text:
        raise HTTPException(status_code=400, detail="Post text cannot be empty.")

    post = Post(text=cleaned_text, user_id=user_id)
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


def attach_image(session: Session, post: Post, file_name: str, file_path: str) -> PostImage:
    post_image = PostImage(
        post_id=post.id,
        file_name=file_name,
        file_path=file_path,
    )
    session.add(post_image)
    session.commit()
    session.refresh(post_image)
    session.refresh(post)
    return post_image
