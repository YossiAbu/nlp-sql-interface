export interface User {
  email: string;
  full_name: string;
}

export const UserAPI = {
  // Returns `null` when unauthenticated
  async me(): Promise<User | null> {
    const res = await fetch("http://localhost:8000/me", {
      method: "GET",
      credentials: "include",
    });

    // If backend ever returns non-200, treat as anonymous
    if (!res.ok) return null;

    const data = await res.json();

    // Backend returns { email: null, full_name: null } when not logged in
    if (!data?.email) return null;

    return {
      email: data.email,
      full_name: data.full_name ?? "",
    };
  },
};
