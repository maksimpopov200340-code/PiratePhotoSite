from fastapi import HTTPException
from sqlmodel import Session, select

from ..models import Comment


def list_comments_for_post(session: Session, post_id: int) -> list[Comment]:
    statement = (
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
    )
    return list(session.exec(statement))


def create_comment(session: Session, post_id: int, user_id: int, text: str) -> Comment:
    cleaned_text = text.strip()
    if not cleaned_text:
        raise HTTPException(status_code=400, detail="Comment text cannot be empty.")

    comment = Comment(
        text=cleaned_text,
        user_id=user_id,
        post_id=post_id,
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment
