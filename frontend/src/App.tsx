import { startTransition, useDeferredValue, useEffect, useState } from "react";

import {
  createComment,
  createPost,
  createUser,
  fetchPost,
  fetchPosts,
  fetchUsers,
} from "./api";
import { ImageLightbox } from "./components/ImageLightbox";
import { PostCard } from "./components/PostCard";
import { PostComposer } from "./components/PostComposer";
import { UserPanel } from "./components/UserPanel";
import type { PostListItem, PostRead, UserRead } from "./types";


const SELECTED_USER_STORAGE_KEY = "pirate-photo-site:selected-user";
type AppPage = "feed" | "compose" | "people";
type FeedFilter = "all" | "photos" | "mine" | "discussed";


function readStoredUserId(): number | null {
  if (typeof window === "undefined") {
    return null;
  }

  const rawValue = window.localStorage.getItem(SELECTED_USER_STORAGE_KEY);
  if (!rawValue) {
    return null;
  }

  const parsedValue = Number(rawValue);
  return Number.isFinite(parsedValue) ? parsedValue : null;
}


function toListItem(post: PostRead): PostListItem {
  return {
    id: post.id,
    text: post.text,
    created_at: post.created_at,
    author: post.author,
    image_url: post.image_url,
    comment_count: post.comments.length,
  };
}


const navigationItems: Array<{ id: AppPage; label: string }> = [
  { id: "feed", label: "Лента" },
  { id: "compose", label: "Публикация" },
  { id: "people", label: "Авторы" },
];


const filterItems: Array<{ id: FeedFilter; label: string }> = [
  { id: "all", label: "Все" },
  { id: "photos", label: "С фото" },
  { id: "mine", label: "Мои" },
  { id: "discussed", label: "С обсуждением" },
];


export default function App() {
  const [activePage, setActivePage] = useState<AppPage>("feed");
  const [users, setUsers] = useState<UserRead[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<number | null>(
    readStoredUserId(),
  );
  const [posts, setPosts] = useState<PostListItem[]>([]);
  const [postDetails, setPostDetails] = useState<Record<number, PostRead>>({});
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [usersError, setUsersError] = useState<string | null>(null);
  const [feedError, setFeedError] = useState<string | null>(null);
  const [isUsersLoading, setIsUsersLoading] = useState(true);
  const [isFeedLoading, setIsFeedLoading] = useState(true);
  const [isCreatingUser, setIsCreatingUser] = useState(false);
  const [isCreatingPost, setIsCreatingPost] = useState(false);
  const [commentingPostId, setCommentingPostId] = useState<number | null>(null);
  const [feedFilter, setFeedFilter] = useState<FeedFilter>("all");
  const [searchQuery, setSearchQuery] = useState("");

  const deferredPosts = useDeferredValue(posts);
  const deferredQuery = useDeferredValue(searchQuery.trim().toLowerCase());
  const currentUser =
    users.find((candidate) => candidate.id === selectedUserId) ?? null;
  const filteredPosts = deferredPosts.filter((post) => {
    const matchesQuery =
      !deferredQuery ||
      post.text.toLowerCase().includes(deferredQuery) ||
      post.author.username.toLowerCase().includes(deferredQuery);

    if (!matchesQuery) {
      return false;
    }

    if (feedFilter === "photos") {
      return Boolean(post.image_url);
    }

    if (feedFilter === "mine") {
      return currentUser ? post.author.id === currentUser.id : false;
    }

    if (feedFilter === "discussed") {
      return post.comment_count > 0;
    }

    return true;
  });

  useEffect(() => {
    void refreshData();
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    if (selectedUserId === null) {
      window.localStorage.removeItem(SELECTED_USER_STORAGE_KEY);
      return;
    }

    window.localStorage.setItem(
      SELECTED_USER_STORAGE_KEY,
      String(selectedUserId),
    );
  }, [selectedUserId]);

  async function loadUsers() {
    setIsUsersLoading(true);
    setUsersError(null);

    try {
      const nextUsers = await fetchUsers();
      startTransition(() => {
        setUsers(nextUsers);
        setSelectedUserId((current) => {
          if (current && nextUsers.some((user) => user.id === current)) {
            return current;
          }

          return nextUsers[0]?.id ?? null;
        });
      });
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Не удалось загрузить авторов.";
      setUsersError(message);
    } finally {
      setIsUsersLoading(false);
    }
  }

  async function loadFeed() {
    setIsFeedLoading(true);
    setFeedError(null);

    try {
      const nextPosts = await fetchPosts();
      const detailEntries = await Promise.all(
        nextPosts.map(async (post) => {
          try {
            const detail = await fetchPost(post.id);
            return [post.id, detail] as const;
          } catch {
            return null;
          }
        }),
      );

      const nextDetails = Object.fromEntries(
        detailEntries.filter(
          (entry): entry is readonly [number, PostRead] => entry !== null,
        ),
      );

      startTransition(() => {
        setPosts(nextPosts);
        setPostDetails(nextDetails);
      });
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Не удалось загрузить ленту.";
      setFeedError(message);
    } finally {
      setIsFeedLoading(false);
    }
  }

  async function refreshData() {
    await Promise.all([loadUsers(), loadFeed()]);
  }

  async function handleCreateUser(username: string, password: string) {
    setIsCreatingUser(true);

    try {
      const user = await createUser({ username, password });
      startTransition(() => {
        setUsers((current) => [...current, user]);
        setSelectedUserId(user.id);
      });
    } finally {
      setIsCreatingUser(false);
    }
  }

  async function handleCreatePost(text: string, image: File | null) {
    if (!currentUser) {
      throw new Error("Сначала выбери автора.");
    }

    setIsCreatingPost(true);

    try {
      const post = await createPost({
        userId: currentUser.id,
        text,
        image,
      });

      startTransition(() => {
        setPosts((current) => [toListItem(post), ...current]);
        setPostDetails((current) => ({
          [post.id]: post,
          ...current,
        }));
        setActivePage("feed");
      });
    } finally {
      setIsCreatingPost(false);
    }
  }

  async function handleCreateComment(postId: number, text: string) {
    if (!currentUser) {
      throw new Error("Сначала выбери автора.");
    }

    setCommentingPostId(postId);

    try {
      const comment = await createComment(postId, {
        user_id: currentUser.id,
        text,
      });

      startTransition(() => {
        setPostDetails((current) => {
          const existingPost = current[postId];
          const basePost = posts.find((post) => post.id === postId);

          if (!existingPost && !basePost) {
            return current;
          }

          if (!existingPost && basePost) {
            return {
              ...current,
              [postId]: {
                id: basePost.id,
                text: basePost.text,
                created_at: basePost.created_at,
                author: basePost.author,
                image_url: basePost.image_url,
                comments: [comment],
              },
            };
          }

          return {
            ...current,
            [postId]: {
              ...existingPost!,
              comments: [...existingPost!.comments, comment],
            },
          };
        });

        setPosts((current) =>
          current.map((post) =>
            post.id === postId
              ? { ...post, comment_count: post.comment_count + 1 }
              : post,
          ),
        );
      });
    } finally {
      setCommentingPostId(null);
    }
  }

  return (
    <>
      <div className="app-shell">
        <header className="topbar">
          <div className="topbar__inner">
            <button
              className="topbar__brand"
              type="button"
              onClick={() => setActivePage("feed")}
            >
              PiratePhoto
            </button>

            <label className="topbar__search">
              <input
                className="topbar__search-input"
                placeholder="Поиск"
                value={searchQuery}
                onChange={(event) => {
                  setSearchQuery(event.target.value);
                  if (activePage !== "feed") {
                    setActivePage("feed");
                  }
                }}
              />
            </label>

            <nav className="topbar__actions">
              {navigationItems.map((item) => (
                <button
                  key={item.id}
                  className={
                    item.id === activePage
                      ? "topbar__nav-button topbar__nav-button--active"
                      : "topbar__nav-button"
                  }
                  type="button"
                  onClick={() => setActivePage(item.id)}
                >
                  {item.label}
                </button>
              ))}
            </nav>
          </div>
        </header>

        <main className="layout">
          <section className="content">
            {usersError ? <p className="banner banner--error">{usersError}</p> : null}
            {feedError ? <p className="banner banner--error">{feedError}</p> : null}
            {isUsersLoading ? <p className="banner">Загружаем пользователей...</p> : null}

            {activePage === "feed" ? (
              <>
                {users.length ? (
                  <div className="stories-strip">
                    {users.map((user) => (
                      <button
                        key={user.id}
                        className={
                          user.id === selectedUserId
                            ? "story-chip story-chip--active"
                            : "story-chip"
                        }
                        type="button"
                        onClick={() => setSelectedUserId(user.id)}
                      >
                        <span className="story-chip__avatar">
                          {user.username.charAt(0).toUpperCase()}
                        </span>
                        <span className="story-chip__name">{user.username}</span>
                      </button>
                    ))}
                  </div>
                ) : null}

                <div className="feed-filters">
                  {filterItems.map((item) => {
                    const isDisabled = item.id === "mine" && !currentUser;

                    return (
                      <button
                        key={item.id}
                        className={
                          item.id === feedFilter
                            ? "filter-chip filter-chip--active"
                            : "filter-chip"
                        }
                        disabled={isDisabled}
                        type="button"
                        onClick={() => setFeedFilter(item.id)}
                      >
                        {item.label}
                      </button>
                    );
                  })}
                </div>

                {isFeedLoading ? (
                  <div className="skeleton-stack">
                    {Array.from({ length: 3 }).map((_, index) => (
                      <div className="post-skeleton" key={index}>
                        <div className="post-skeleton__line post-skeleton__line--short" />
                        <div className="post-skeleton__media" />
                        <div className="post-skeleton__line" />
                      </div>
                    ))}
                  </div>
                ) : filteredPosts.length ? (
                  <div className="feed-column">
                    {filteredPosts.map((post) => (
                      <PostCard
                        key={post.id}
                        post={post}
                        detail={postDetails[post.id]}
                        currentUser={currentUser}
                        isSubmittingComment={commentingPostId === post.id}
                        onOpenImage={setImageUrl}
                        onCreateComment={handleCreateComment}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">
                    <h3>Ничего не найдено</h3>
                    <p>Попробуй изменить поиск или опубликовать новый пост.</p>
                  </div>
                )}
              </>
            ) : null}

            {activePage === "compose" ? (
              <div className="page-card">
                <PostComposer
                  currentUser={currentUser}
                  isSubmitting={isCreatingPost}
                  onCreatePost={handleCreatePost}
                />
              </div>
            ) : null}

            {activePage === "people" ? (
              <div className="page-card page-card--narrow">
                <UserPanel
                  users={users}
                  selectedUserId={selectedUserId}
                  currentUser={currentUser}
                  isSubmitting={isCreatingUser}
                  onSelectUser={setSelectedUserId}
                  onCreateUser={handleCreateUser}
                />
              </div>
            ) : null}
          </section>

          <aside className="sidebar">
            <div className="sidebar-shell">
              <button
                className="sidebar-profile"
                type="button"
                onClick={() => setActivePage("people")}
              >
                <span className="sidebar-profile__avatar">
                  {currentUser?.username?.charAt(0).toUpperCase() ?? "+"}
                </span>
                <span className="sidebar-profile__body">
                  <span className="sidebar-profile__name">
                    {currentUser?.username ?? "Создать автора"}
                  </span>
                  <span className="sidebar-profile__action">
                    {currentUser ? "Сменить" : "Открыть"}
                  </span>
                </span>
              </button>

              {activePage === "feed" ? (
                <div className="sidebar-section">
                  <div className="chip-grid chip-grid--sidebar">
                    {filterItems.map((item) => {
                      const isDisabled = item.id === "mine" && !currentUser;

                      return (
                        <button
                          key={item.id}
                          className={
                            item.id === feedFilter
                              ? "filter-chip filter-chip--active"
                              : "filter-chip"
                          }
                          disabled={isDisabled}
                          type="button"
                          onClick={() => setFeedFilter(item.id)}
                        >
                          {item.label}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ) : null}

              {users.length ? (
                <div className="sidebar-users">
                  {users.map((user) => (
                    <button
                      key={user.id}
                      className={
                        user.id === selectedUserId
                          ? "sidebar-user sidebar-user--active"
                          : "sidebar-user"
                      }
                      type="button"
                      onClick={() => setSelectedUserId(user.id)}
                    >
                      <span className="sidebar-user__avatar">
                        {user.username.charAt(0).toUpperCase()}
                      </span>
                      <span className="sidebar-user__name">{user.username}</span>
                    </button>
                  ))}
                </div>
              ) : null}

              <button
                className="sidebar-link"
                type="button"
                onClick={() => void refreshData()}
              >
                Обновить
              </button>
            </div>
          </aside>
        </main>

        <nav className="mobile-nav">
          {navigationItems.map((item) => (
            <button
              key={item.id}
              className={
                item.id === activePage
                  ? "mobile-nav__button mobile-nav__button--active"
                  : "mobile-nav__button"
              }
              type="button"
              onClick={() => setActivePage(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </div>

      <ImageLightbox imageUrl={imageUrl} onClose={() => setImageUrl(null)} />
    </>
  );
}
