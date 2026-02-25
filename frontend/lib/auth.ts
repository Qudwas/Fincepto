import { api } from "./api";

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  company_id: string | null;
}

export async function login(credentials: LoginCredentials): Promise<AuthTokens> {
  const tokens = await api.post<AuthTokens>("/auth/login", credentials);
  if (typeof window !== "undefined") {
    localStorage.setItem("access_token", tokens.access_token);
    localStorage.setItem("refresh_token", tokens.refresh_token);
  }
  return tokens;
}

export async function logout(): Promise<void> {
  try {
    await api.post("/auth/logout", {});
  } catch {}
  if (typeof window !== "undefined") {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }
}

export async function getCurrentUser(): Promise<User> {
  return api.get<User>("/auth/me");
}

export function isAuthenticated(): boolean {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("access_token");
}
