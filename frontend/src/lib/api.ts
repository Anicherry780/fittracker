import Cookies from "js-cookie";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiClient {
  private getToken(): string | undefined {
    return Cookies.get("token");
  }

  private headers(isFormData = false): HeadersInit {
    const headers: HeadersInit = {};
    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    if (!isFormData) {
      headers["Content-Type"] = "application/json";
    }
    return headers;
  }

  async get<T>(path: string): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: this.headers(),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail || "Request failed");
    }
    return res.json();
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: this.headers(),
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail || "Request failed");
    }
    return res.json();
  }

  async postForm<T>(path: string, formData: FormData): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: this.headers(true),
      body: formData,
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail || "Request failed");
    }
    return res.json();
  }

  async patch<T>(path: string, body: unknown): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, {
      method: "PATCH",
      headers: this.headers(),
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail || "Request failed");
    }
    return res.json();
  }

  async delete(path: string): Promise<void> {
    const res = await fetch(`${API_BASE}${path}`, {
      method: "DELETE",
      headers: this.headers(),
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail || "Request failed");
    }
  }
}

export const api = new ApiClient();
