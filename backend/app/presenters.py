from .models import Comment, Post, User
from .schemas import CommentRead, PostListItem, PostRead, UserRead
from .storage import build_media_url


def to_user_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        username=user.username,
        created_at=user.created_at,
    )


def to_comment_read(comment: Comment) -> CommentRead:
    return CommentRead(
        id=comment.id,
        text=comment.text,
        created_at=comment.created_at,
        author=to_user_read(comment.author),
    )


def to_post_list_item(post: Post) -> PostListItem:
    first_image = post.images[0] if post.images else None

    return PostListItem(
        id=post.id,
        text=post.text,
        created_at=post.created_at,
        author=to_user_read(post.author),
        image_url=build_media_url(first_image.file_path if first_image else None),
        comment_count=len(post.comments),
    )


def to_post_read(post: Post) -> PostRead:
    first_image = post.images[0] if post.images else None

    return PostRead(
        id=post.id,
        text=post.text,
        created_at=post.created_at,
        author=to_user_read(post.author),
        image_url=build_media_url(first_image.file_path if first_image else None),
        comments=[to_comment_read(comment) for comment in post.comments],
    )
