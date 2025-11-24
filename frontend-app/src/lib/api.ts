// export async function fetchQuery(question: string) {
//   const reponse = await fetch("http://localhost:8000/query", {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     credentials: "include",
//     body: JSON.stringify({ question }),
//   });
//   if (!reponse.ok) throw new Error("Query failed");
//   return reponse.json();
// }

// export async function fetchHistory(page: number = 1, per_page: number = 20) {
//   const response = await fetch(`http://localhost:8000/history?page=${page}&per_page=${per_page}`, {
//     method: "GET",
//     credentials: "include",
//   });
//   if (!response.ok) throw new Error("Failed to fetch history");
//   return response.json();
// }

// export async function clearHistory() {
//   const response = await fetch("http://localhost:8000/history", {
//     method: "DELETE",
//     credentials: "include",
//   });
//   if (!response.ok) throw new Error("Failed to clear history");
//   return response.json();
// }


const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

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
