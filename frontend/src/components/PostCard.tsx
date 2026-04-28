import { useState } from "react";

import type { PostListItem, PostRead, UserRead } from "../types";
import { formatDateTime, getUserInitial } from "../utils";


interface PostCardProps {
  post: PostListItem;
  detail?: PostRead;
  currentUser: UserRead | null;
  isSubmittingComment: boolean;
  onOpenImage: (imageUrl: string) => void;
  onCreateComment: (postId: number, text: string) => Promise<void>;
}


export function PostCard({
  post,
  detail,
  currentUser,
  isSubmittingComment,
  onOpenImage,
  onCreateComment,
}: PostCardProps) {
  const [commentText, setCommentText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [showAllComments, setShowAllComments] = useState(false);
  const comments = detail?.comments ?? [];
  const visibleComments = showAllComments ? comments : comments.slice(-2);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    try {
      await onCreateComment(post.id, commentText);
      setCommentText("");
    } catch (submitError) {
      const message =
        submitError instanceof Error
          ? submitError.message
          : "Не удалось отправить комментарий.";
      setError(message);
    }
  }

  return (
    <article className="post-card">
      <header className="post-card__header">
        <div className="identity-card identity-card--compact">
          <div className="identity-card__avatar">
            {getUserInitial(post.author.username)}
          </div>
          <div>
            <div className="identity-card__name">{post.author.username}</div>
            <div className="identity-card__meta">
              {formatDateTime(post.created_at)}
            </div>
          </div>
        </div>
      </header>

      {post.image_url ? (
        <div className="post-card__media">
          <button
            className="post-card__image-button"
            type="button"
            onClick={() => onOpenImage(post.image_url!)}
          >
            <img
              className="post-card__image"
              src={post.image_url}
              alt={post.text}
              loading="lazy"
            />
          </button>
        </div>
      ) : null}

      <section className="post-card__body">
        <p className="post-card__caption">
          <strong>{post.author.username}</strong> {post.text}
        </p>

        {comments.length > 2 ? (
          <button
            className="comment-toggle"
            type="button"
            onClick={() => setShowAllComments((current) => !current)}
          >
            {showAllComments
              ? "Скрыть комментарии"
              : "Показать комментарии"}
          </button>
        ) : null}

        {visibleComments.length ? (
          <div className="comment-list">
            {visibleComments.map((comment) => (
              <div className="comment" key={comment.id}>
                <div className="comment__body">
                  <div className="comment__meta">
                    <strong>{comment.author.username}</strong>
                    <span>{formatDateTime(comment.created_at)}</span>
                  </div>
                  <p>{comment.text}</p>
                </div>
              </div>
            ))}
          </div>
        ) : null}

        <form className="comment-form" onSubmit={handleSubmit}>
          <input
            className="field__control"
            placeholder={
              currentUser
                ? "Добавить комментарий..."
                : "Сначала выбери автора"
            }
            value={commentText}
            onChange={(event) => setCommentText(event.target.value)}
          />
          <button
            className="secondary-button"
            disabled={isSubmittingComment || !currentUser}
            type="submit"
          >
            {isSubmittingComment ? "..." : "Отправить"}
          </button>
        </form>

        {error ? <p className="form-error">{error}</p> : null}
      </section>
    </article>
  );
}
