import type { CommentRead, PostListItem, PostRead, UserRead } from "./types";


interface ApiErrorPayload {
  detail?: string;
}


interface CreateUserPayload {
  username: string;
  password: string;
}


interface CreatePostPayload {
  userId: number;
  text: string;
  image?: File | null;
}


interface CreateCommentPayload {
  user_id: number;
  text: string;
}


async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);

  if (!response.ok) {
    let message = `Request failed with status ${response.status}.`;

    try {
      const payload = (await response.json()) as ApiErrorPayload;
      if (payload.detail) {
        message = payload.detail;
      }
    } catch {
      message = response.statusText || message;
    }

    throw new Error(message);
  }

  return (await response.json()) as T;
}


export function fetchUsers(): Promise<UserRead[]> {
  return request<UserRead[]>("/api/users/");
}


export function createUser(payload: CreateUserPayload): Promise<UserRead> {
  return request<UserRead>("/api/users/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}


export function fetchPosts(): Promise<PostListItem[]> {
  return request<PostListItem[]>("/api/posts/");
}


export function fetchPost(postId: number): Promise<PostRead> {
  return request<PostRead>(`/api/posts/${postId}`);
}


export function createPost(payload: CreatePostPayload): Promise<PostRead> {
  const formData = new FormData();
  formData.append("user_id", String(payload.userId));
  formData.append("text", payload.text);

  if (payload.image) {
    formData.append("image", payload.image);
  }

  return request<PostRead>("/api/posts/", {
    method: "POST",
    body: formData,
  });
}


export function createComment(
  postId: number,
  payload: CreateCommentPayload,
): Promise<CommentRead> {
  return request<CommentRead>(`/api/posts/${postId}/comments/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}
