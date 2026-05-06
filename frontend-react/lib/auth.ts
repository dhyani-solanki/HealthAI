export const TOKEN_KEY = "health_token";
export const USER_KEY = "health_user";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setAuth(token: string, userName: string): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, userName);
}

export function clearAuth(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getUserName(): string {
  if (typeof window === "undefined") return "User";
  return localStorage.getItem(USER_KEY) || "User";
}

export function isLoggedIn(): boolean {
  return Boolean(getToken());
}

export function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/);
  return (parts[0][0] + (parts[1]?.[0] ?? "")).toUpperCase();
}
