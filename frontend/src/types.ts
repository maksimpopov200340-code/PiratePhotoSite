export interface UserRead {
  id: number;
  username: string;
  created_at: string;
}


export interface CommentRead {
  id: number;
  text: string;
  created_at: string;
  author: UserRead;
}


export interface PostListItem {
  id: number;
  text: string;
  created_at: string;
  author: UserRead;
  image_url: string | null;
  comment_count: number;
}


export interface PostRead {
  id: number;
  text: string;
  created_at: string;
  author: UserRead;
  image_url: string | null;
  comments: CommentRead[];
}
