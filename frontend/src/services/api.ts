const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

function getToken(): string | null {
  return localStorage.getItem("access_token");
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const message =
      typeof err.detail === "string"
        ? err.detail
        : err.detail?.message || JSON.stringify(err.detail) || "Request failed";

    throw new Error(message);
  }

  return res.json();
}

// Auth

export const api = {
  auth: {
    register: (email: string, full_name: string, password: string) =>
      request<{ access_token: string; refresh_token: string }>(
        "/auth/register",
        {
          method: "POST",
          body: JSON.stringify({ email, full_name, password }),
        },
      ),

    login: (email: string, password: string) =>
      request<{ access_token: string; refresh_token: string }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }),

    me: () =>
      request<{ id: number; email: string; full_name: string }>("/auth/me"),
  },

  // Boards
  boards: {
    list: () => request<Board[]>("/boards"),
    get: (id: number) => request<BoardDetail>(`/boards/${id}`),
    create: (name: string) =>
      request<Board>("/boards", {
        method: "POST",
        body: JSON.stringify({ name }),
      }),
  },

  // Cards
  cards: {
    create: (boardId: number, data: Partial<Card>) =>
      request<Card>(`/boards/${boardId}/cards`, {
        method: "POST",
        body: JSON.stringify(data),
      }),

    update: (boardId: number, cardId: number, data: Partial<Card>) =>
      request<Card>(`/boards/${boardId}/cards/${cardId}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      }),

    delete: (boardId: number, cardId: number) =>
      request(`/boards/${boardId}/cards/${cardId}`, { method: "DELETE" }),
  },
};

// Types
export interface Card {
  id: number;
  title: string;
  description?: string;
  tag?: string;
  column_id: number;
  position: number;
  assignee_id?: number;
}

export interface Column {
  id: number;
  title: string;
  position: number;
  cards: Card[];
}

export interface Board {
  id: number;
  name: string;
  owner_id: number;
}

export interface BoardDetail extends Board {
  columns: Column[];
}
