import Cookies from "js-cookie";

export interface User {
  id: string;
  username: string;
  email: string;
  weight_kg: number | null;
  height_cm: number | null;
  age: number | null;
  gender: string | null;
  activity_level: number | null;
  calorie_target: number | null;
  created_at: string;
}

export function setAuth(token: string, user: User) {
  Cookies.set("token", token, { expires: 1 }); // 1 day
  localStorage.setItem("user", JSON.stringify(user));
}

export function getUser(): User | null {
  if (typeof window === "undefined") return null;
  const data = localStorage.getItem("user");
  return data ? JSON.parse(data) : null;
}

export function getToken(): string | undefined {
  return Cookies.get("token");
}

export function logout() {
  Cookies.remove("token");
  localStorage.removeItem("user");
  window.location.href = "/login";
}

export function isAuthenticated(): boolean {
  return !!getToken();
}
