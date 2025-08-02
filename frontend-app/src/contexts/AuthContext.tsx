import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";

/* ------------------------------------------------------------------ */
/* Types                                                              */
/* ------------------------------------------------------------------ */
export interface User {
  id: string;
  name: string;
  email?: string;
}

/* What the context will expose */
interface AuthContextShape {
  user: User | null;
  login: (u: User) => void;
  logout: () => void;
}

/* ------------------------------------------------------------------ */
/* Context + helper hook                                              */
/* ------------------------------------------------------------------ */
const AuthContext = createContext<AuthContextShape | undefined>(undefined);

export const useAuth = (): AuthContextShape => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
};

/* ------------------------------------------------------------------ */
/* Provider                                                           */
/* ------------------------------------------------------------------ */
interface Props {
  children: ReactNode;
}

export function AuthProvider({ children }: Props) {
  const [user, setUser] = useState<User | null>(null);

  /* keep user in localStorage so it survives refresh */
  useEffect(() => {
    const stored = window.localStorage.getItem("demo-auth-user");
    if (stored) setUser(JSON.parse(stored));
  }, []);

  const login = (u: User) => {
    setUser(u);
    window.localStorage.setItem("demo-auth-user", JSON.stringify(u));
  };

  const logout = () => {
    setUser(null);
    window.localStorage.removeItem("demo-auth-user");
  };

  const value: AuthContextShape = { user, login, logout };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
