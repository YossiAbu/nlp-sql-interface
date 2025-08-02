export interface User {
  email: string;
  full_name?: string; // ✅ add this field to fix Error #2
}

export const UserAPI = {
  async me(): Promise<User> {
    return {
      email: "demo@example.com",
      full_name: "Demo User"
    };
  },
  async login(): Promise<void> {
    alert("Simulated login");
  },
  async logout(): Promise<void> {
    alert("Simulated logout");
  }
};
