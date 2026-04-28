import { useEffect, useState } from "react";

import type { UserRead } from "../types";


interface PostComposerProps {
  currentUser: UserRead | null;
  isSubmitting: boolean;
  onCreatePost: (text: string, image: File | null) => Promise<void>;
}


export function PostComposer({
  currentUser,
  isSubmitting,
  onCreatePost,
}: PostComposerProps) {
  const [text, setText] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!image) {
      setPreviewUrl(null);
      return;
    }

    const url = URL.createObjectURL(image);
    setPreviewUrl(url);

    return () => URL.revokeObjectURL(url);
  }, [image]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    try {
      await onCreatePost(text, image);
      setText("");
      setImage(null);
    } catch (submitError) {
      const message =
        submitError instanceof Error
          ? submitError.message
          : "Не удалось создать пост.";
      setError(message);
    }
  }

  return (
    <section className="panel panel--page panel--compose">
      <div className="panel__header">
        <h2 className="panel__title">Новый пост</h2>
      </div>

      <form className="stack" onSubmit={handleSubmit}>
        {currentUser ? (
          <div className="compose-user">{currentUser.username}</div>
        ) : null}

        <label className="field">
          <textarea
            className="field__control field__control--textarea"
            placeholder="Подпись к публикации"
            value={text}
            onChange={(event) => setText(event.target.value)}
          />
        </label>

        <label className="upload-tile" htmlFor="image-upload">
          <input
            id="image-upload"
            className="upload-tile__input"
            type="file"
            accept="image/png,image/jpeg,image/webp"
            onChange={(event) => setImage(event.target.files?.[0] ?? null)}
          />
          <span className="upload-tile__title">Выбрать изображение</span>
          <span className="upload-tile__subtitle">PNG, JPG или WEBP</span>
        </label>

        {previewUrl ? (
          <div className="composer-preview">
            <img className="composer-preview__image" src={previewUrl} alt="Preview" />
            <button
              className="ghost-button ghost-button--light"
              type="button"
              onClick={() => setImage(null)}
            >
              Убрать изображение
            </button>
          </div>
        ) : null}

        {error ? <p className="form-error">{error}</p> : null}

        <button
          className="primary-button"
          disabled={isSubmitting || !currentUser}
          type="submit"
        >
          {isSubmitting
            ? "Публикуем..."
            : currentUser
              ? "Опубликовать"
              : "Сначала выбери автора"}
        </button>
      </form>
    </section>
  );
}
