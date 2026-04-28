import { useEffect, useState } from "react";

import type { UserRead } from "../types";
import { getUserInitial } from "../utils";


interface UserPanelProps {
  users: UserRead[];
  selectedUserId: number | null;
  currentUser: UserRead | null;
  isSubmitting: boolean;
  onSelectUser: (userId: number | null) => void;
  onCreateUser: (username: string, password: string) => Promise<void>;
}


export function UserPanel({
  users,
  selectedUserId,
  currentUser,
  isSubmitting,
  onSelectUser,
  onCreateUser,
}: UserPanelProps) {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (users.length === 0) {
      setShowCreateForm(true);
    }
  }, [users.length]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    try {
      await onCreateUser(username, password);
      setUsername("");
      setPassword("");
      setShowCreateForm(false);
    } catch (submitError) {
      const message =
        submitError instanceof Error
          ? submitError.message
          : "Не удалось создать автора.";
      setError(message);
    }
  }

  return (
    <section className="panel panel--page">
      <div className="panel__header">
        <h2 className="panel__title">Авторы</h2>
        <button
          className="ghost-button"
          type="button"
          onClick={() => setShowCreateForm((current) => !current)}
        >
          {showCreateForm ? "Скрыть форму" : "Новый пользователь"}
        </button>
      </div>

      {currentUser ? (
        <div className="identity-card identity-card--selected">
          <div className="identity-card__avatar">
            {getUserInitial(currentUser.username)}
          </div>
          <div className="identity-card__name">{currentUser.username}</div>
        </div>
      ) : null}

      <div className="user-grid">
        {users.map((user) => (
          <button
            key={user.id}
            className={
              user.id === selectedUserId
                ? "user-chip user-chip--active"
                : "user-chip"
            }
            type="button"
            onClick={() => onSelectUser(user.id)}
          >
            <span className="user-chip__avatar">{getUserInitial(user.username)}</span>
            <span className="user-chip__content">
              <span className="user-chip__name">{user.username}</span>
            </span>
          </button>
        ))}
      </div>

      {showCreateForm ? (
        <form className="stack" onSubmit={handleSubmit}>
          <label className="field">
            <input
              className="field__control"
              placeholder="Имя"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
            />
          </label>

          <label className="field">
            <input
              className="field__control"
              type="password"
              placeholder="Пароль"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>

          {error ? <p className="form-error">{error}</p> : null}

          <button className="primary-button" disabled={isSubmitting} type="submit">
            {isSubmitting ? "Создаем..." : "Создать пользователя"}
          </button>
        </form>
      ) : null}
    </section>
  );
}
