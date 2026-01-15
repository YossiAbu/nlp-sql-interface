export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
export const FRONTEND_BASE_URL = import.meta.env.VITE_FRONTEND_BASE_URL ?? "http://localhost:5173";

async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function fetchQuery(question: string) {
  return apiRequest("/query", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

export function fetchHistory(page = 1, per_page = 20) {
  return apiRequest(`/history?page=${page}&per_page=${per_page}`);
}

export function clearHistory() {
  return apiRequest("/history", { method: "DELETE" });
}
