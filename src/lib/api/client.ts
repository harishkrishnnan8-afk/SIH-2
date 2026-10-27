// Central API client for the APAAR backend (/api/v1).
// UI reads data only via src/lib/services.
// Flip BACKEND_CONNECTED to swap between real backend and synthetic fallback.
let envApiBase = (typeof import.meta !== "undefined" && import.meta.env?.VITE_API_BASE_URL)
  ? String(import.meta.env.VITE_API_BASE_URL).trim()
  : "";

if (envApiBase && !envApiBase.startsWith("http://") && !envApiBase.startsWith("https://") && !envApiBase.startsWith("/")) {
  envApiBase = `https://${envApiBase}`;
}

export const API_BASE = envApiBase
  ? (envApiBase.replace(/\/+$/, "").endsWith("/api/v1")
      ? envApiBase.replace(/\/+$/, "")
      : `${envApiBase.replace(/\/+$/, "")}/api/v1`)
  : (typeof window !== "undefined" && window.location.hostname !== "localhost"
      ? "/api/v1"
      : "http://127.0.0.1:8000/api/v1");


export const BACKEND_CONNECTED = true;

const TOKEN_KEY = "apaar_auth_token";
const USER_KEY = "apaar_auth_user";

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setAuthSession(token: string, user: object) {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearAuthSession() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getStoredUser<T>(): T | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    ...(init?.headers as Record<string, string> ?? {}),
  };

  // Only set application/json if not sending FormData
  if (!(init?.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  if (token && !headers["Authorization"]) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers,
      credentials: "include",
    });

    if (!res.ok) {
      let errorMsg = `Request failed (${res.status})`;
      try {
        const errJson = await res.json();
        if (errJson && errJson.detail) {
          errorMsg = typeof errJson.detail === "string" ? errJson.detail : JSON.stringify(errJson.detail);
        }
      } catch {
        // fallback to status code message
      }
      throw new ApiError(res.status, errorMsg);
    }

    return (await res.json()) as T;
  } catch (err: unknown) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(0, err instanceof Error ? err.message : "Network error. Backend unreachable.");
  }
}

/** Mask an APAAR identifier, revealing only the last 4 digits. */
export function maskApaar(id: string): string {
  const digits = id.replace(/\D/g, "");
  if (digits.length < 4) return "•••• •••• ••••";
  return `•••• •••• ${digits.slice(-4)}`;
}
