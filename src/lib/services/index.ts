// Service layer. Each function maps to an /api/v1 endpoint.
// When BACKEND_CONNECTED is true, requests hit the FastAPI backend.
// When false or in testing without server, fallback to demo dataset.
import { queryOptions } from "@tanstack/react-query";
import { BACKEND_CONNECTED, apiRequest, setAuthSession, clearAuthSession, ApiError } from "@/lib/api/client";
import * as demo from "@/lib/demo/data";

const delay = <T,>(v: T, ms = 350) => new Promise<T>((r) => setTimeout(() => r(v), ms));

async function get<T>(path: string, fallback: T): Promise<T> {
  if (!BACKEND_CONNECTED) return delay(fallback);
  try {
    return await apiRequest<T>(path);
  } catch (err) {
    console.warn(`Backend query failed for ${path}, falling back to demo fixture:`, err);
    return fallback;
  }
}

export const studentsQuery = () => queryOptions({ queryKey: ["students"], queryFn: () => get("/students", demo.students) });
export const studentQuery = (id: string) =>
  queryOptions({ queryKey: ["students", id], queryFn: () => get(`/students/${id}`, demo.students.find((s) => s.id === id) ?? null) });
export const findingsQuery = () => queryOptions({ queryKey: ["findings"], queryFn: () => get("/findings", demo.findings) });
export const importsQuery = () => queryOptions({ queryKey: ["imports"], queryFn: () => get("/uploads", demo.imports) });
export const programmesQuery = () => queryOptions({ queryKey: ["programmes"], queryFn: () => get("/programmes", demo.programmes) });
export const institutionsQuery = () => queryOptions({ queryKey: ["institutions"], queryFn: () => get("/institutions", demo.institutions) });
export const auditQuery = () => queryOptions({ queryKey: ["audit"], queryFn: () => get("/audit", demo.audit) });

export type VerificationResult = {
  mode: "format" | "internal" | "simulated" | "external";
  formatValid: boolean;
  internalMatch: boolean;
  providerStatus: "Mock provider" | "Online" | "Unavailable";
  checkedAt: string;
  student?: demo.Student | undefined;
  isSimulated?: boolean;
  simulationLabel?: string;
};

export async function verifyApaar(id: string): Promise<VerificationResult> {
  if (BACKEND_CONNECTED) {
    try {
      const res = await apiRequest<VerificationResult>("/verification/verify", {
        method: "POST",
        body: JSON.stringify({ id }),
      });
      return res;
    } catch (err) {
      console.warn("Backend verification failed, using local simulation:", err);
    }
  }

  const digits = id.replace(/\D/g, "");
  const student = demo.students.find((s) => s.apaar === digits);
  return delay({
    mode: "simulated",
    formatValid: digits.length === 12,
    internalMatch: !!student,
    providerStatus: "Mock provider",
    checkedAt: new Date().toISOString(),
    student,
    isSimulated: true,
    simulationLabel: "SIMULATED — NOT OFFICIAL APAAR VERIFICATION",
  }, 500);
}

export interface StudentPayload {
  name: string;
  apaar: string;
  programme: string;
  year?: string;
  category?: string;
  status?: string;
  nri?: boolean;
  oci?: boolean;
  ociCard?: string;
  foreign?: boolean;
  nationality?: string;
  dob?: string;
  gender?: string;
  email?: string;
}

export async function saveStudent(payload?: StudentPayload): Promise<{ persisted: boolean; message?: string }> {
  if (BACKEND_CONNECTED && payload) {
    try {
      const res = await apiRequest<{ persisted: boolean; message: string }>("/students", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      return res;
    } catch (err) {
      console.error("Save student failed:", err);
      throw err;
    }
  }
  return delay({ persisted: false, message: "Backend is disconnected" }, 600);
}

export async function recordFindingAction(findingId: string, action: string, note: string) {
  if (BACKEND_CONNECTED) {
    return apiRequest(`/findings/${findingId}/actions`, {
      method: "POST",
      body: JSON.stringify({ action, note }),
    });
  }
  return delay({ success: true });
}

export async function uploadCsvFile(file: File) {
  if (BACKEND_CONNECTED) {
    const formData = new FormData();
    formData.append("file", file);
    return apiRequest<{
      accepted: number;
      rejected: number;
      total: number;
      errors: Array<{ row: number; field: string; value: string; rule: string }>;
      batch_id: string;
      persisted: boolean;
    }>("/uploads", {
      method: "POST",
      body: formData,
    });
  }
  return delay({
    accepted: 0,
    rejected: 0,
    total: 0,
    errors: [],
    batch_id: "BATCH-LOCAL",
    persisted: false,
  });
}

export async function loginUser(user: string, pass: string) {
  if (BACKEND_CONNECTED) {
    const res = await apiRequest<{ access_token: string; token_type: string; user: any }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ user, pass }),
    });
    setAuthSession(res.access_token, res.user);
    return res.user;
  }
  return delay({ username: user, role: "institution_admin", full_name: "Priya Nair" }, 500);
}

export async function logoutUser() {
  if (BACKEND_CONNECTED) {
    try {
      await apiRequest("/auth/logout", { method: "POST" });
    } catch {
      // ignore network errors on logout
    }
  }
  clearAuthSession();
}
