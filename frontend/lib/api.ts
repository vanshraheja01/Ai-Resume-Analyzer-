import type {
  Application,
  ApplicationStatus,
  DashboardStats,
  Job,
  JobExtractedData,
  Match,
  ResumeAnalysis,
  ResumeDetail,
  ResumeSummary,
  User,
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "resume_analyzer_token";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null): void {
  if (typeof window === "undefined") return;
  if (token) window.localStorage.setItem(TOKEN_KEY, token);
  else window.localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(
  path: string,
  options: { method?: string; body?: unknown; form?: FormData; auth?: boolean } = {}
): Promise<T> {
  const { method = "GET", body, form, auth = true } = options;
  const headers: Record<string, string> = {};

  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  let requestBody: BodyInit | undefined;
  if (form) {
    requestBody = form; // browser sets multipart Content-Type + boundary
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    requestBody = JSON.stringify(body);
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { method, headers, body: requestBody });
  } catch {
    throw new ApiError(0, "Could not reach the server. Is the backend running?");
  }

  if (response.status === 204) return undefined as T;

  const text = await response.text();
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    const message =
      typeof data?.detail === "string"
        ? data.detail
        : Array.isArray(data?.detail)
          ? data.detail.map((d: { msg?: string }) => d.msg).join(", ")
          : `Request failed (${response.status})`;
    throw new ApiError(response.status, message);
  }

  return data as T;
}

// --- Auth ---------------------------------------------------------------

export const authApi = {
  register: (data: { email: string; password: string; full_name?: string }) =>
    request<User>("/api/auth/register", { method: "POST", body: data, auth: false }),

  login: async (email: string, password: string) => {
    const form = new URLSearchParams();
    form.set("username", email);
    form.set("password", password);
    const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form.toString(),
    });
    const data = await res.json();
    if (!res.ok) throw new ApiError(res.status, data?.detail ?? "Login failed");
    return data as { access_token: string; token_type: string };
  },

  me: () => request<User>("/api/auth/me"),

  updateProfile: (data: {
    full_name?: string | null;
    location?: string | null;
    github_url?: string | null;
    linkedin_url?: string | null;
    portfolio_url?: string | null;
    preferred_role?: string | null;
  }) => request<User>("/api/auth/me", { method: "PUT", body: data }),
};

// --- Resumes --------------------------------------------------------------

export const resumesApi = {
  upload: (file: File, title?: string) => {
    const form = new FormData();
    form.set("file", file);
    if (title) form.set("title", title);
    return request<ResumeDetail>("/api/resumes/upload", { method: "POST", form });
  },
  list: () => request<ResumeSummary[]>("/api/resumes"),
  get: (id: string) => request<ResumeDetail>(`/api/resumes/${id}`),
  remove: (id: string) => request<void>(`/api/resumes/${id}`, { method: "DELETE" }),
  analyze: (id: string) => request<ResumeAnalysis>(`/api/resumes/${id}/analyze`, { method: "POST" }),
  analyses: (id: string) => request<ResumeAnalysis[]>(`/api/resumes/${id}/analyses`),
};

// --- Jobs -------------------------------------------------------------------

export const jobsApi = {
  analyze: (data: { title: string; company?: string; description_raw: string; job_url?: string }) =>
    request<Job>("/api/jobs/analyze", { method: "POST", body: data }),
  list: () => request<Job[]>("/api/jobs"),
  get: (id: string) => request<Job>(`/api/jobs/${id}`),
  remove: (id: string) => request<void>(`/api/jobs/${id}`, { method: "DELETE" }),
};

export type { JobExtractedData };

// --- Matching -----------------------------------------------------------

export const matchingApi = {
  analyze: (resumeId: string, jobId: string) =>
    request<Match>("/api/matching/analyze", { method: "POST", body: { resume_id: resumeId, job_id: jobId } }),
};

// --- Applications -------------------------------------------------------

export interface ApplicationInput {
  company: string;
  position_title: string;
  status?: ApplicationStatus;
  job_id?: string | null;
  resume_id?: string | null;
  application_date?: string | null;
  interview_date?: string | null;
  job_url?: string | null;
  notes?: string | null;
}

export const applicationsApi = {
  list: (status?: ApplicationStatus) =>
    request<Application[]>(`/api/applications${status ? `?status=${status}` : ""}`),
  create: (data: ApplicationInput) => request<Application>("/api/applications", { method: "POST", body: data }),
  update: (id: string, data: Partial<ApplicationInput>) =>
    request<Application>(`/api/applications/${id}`, { method: "PUT", body: data }),
  remove: (id: string) => request<void>(`/api/applications/${id}`, { method: "DELETE" }),
};

// --- Dashboard ------------------------------------------------------------

export const dashboardApi = {
  get: () => request<DashboardStats>("/api/dashboard"),
};
