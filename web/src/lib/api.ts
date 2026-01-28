/**
 * API client for Jobflow backend.
 * All requests go through Next.js API routes which proxy to the backend.
 */

const API_BASE = "";

export interface Job {
  id: number;
  url: string;
  title: string;
  company: string;
  location: string | null;
  salary: string | null;
  description: string | null;
  extraction_method: string | null;
  flagged: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface JobCreateResult {
  url: string;
  success: boolean;
  job: Job | null;
  error: string | null;
}

export interface JobCreateResponse {
  results: JobCreateResult[];
  total: number;
  succeeded: number;
  failed: number;
}

export interface JobListResponse {
  jobs: Job[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface JobUpdate {
  title?: string;
  company?: string;
  location?: string;
  salary?: string;
  description?: string;
}

export interface ManualJobInput {
  title: string;
  company: string;
  location?: string;
  salary?: string;
  description?: string;
  url?: string;
}

export interface ParsedJobFields {
  title: string | null;
  company: string | null;
  location: string | null;
  salary: string | null;
}

class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    throw new ApiError(response.status, text || response.statusText);
  }
  return response.json();
}

export async function createJobs(urls: string[]): Promise<JobCreateResponse> {
  const response = await fetch(`${API_BASE}/api/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ urls }),
  });
  return handleResponse<JobCreateResponse>(response);
}

export async function createJobManual(job: ManualJobInput): Promise<Job> {
  const response = await fetch(`${API_BASE}/api/jobs/manual`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(job),
  });
  return handleResponse<Job>(response);
}

export async function parseJobDescription(text: string): Promise<ParsedJobFields> {
  const response = await fetch(`${API_BASE}/api/jobs/parse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return handleResponse<ParsedJobFields>(response);
}

export async function listJobs(
  page = 1,
  perPage = 20,
  filters?: { company?: string; flagged?: boolean }
): Promise<JobListResponse> {
  const params = new URLSearchParams({
    page: page.toString(),
    per_page: perPage.toString(),
  });
  if (filters?.company) params.set("company", filters.company);
  if (filters?.flagged !== undefined)
    params.set("flagged", filters.flagged.toString());

  const response = await fetch(`${API_BASE}/api/jobs?${params}`);
  return handleResponse<JobListResponse>(response);
}

export async function getJob(id: number): Promise<Job> {
  const response = await fetch(`${API_BASE}/api/jobs/${id}`);
  return handleResponse<Job>(response);
}

export async function updateJob(id: number, data: JobUpdate): Promise<Job> {
  const response = await fetch(`${API_BASE}/api/jobs/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse<Job>(response);
}

export async function flagJob(id: number, flagged: boolean): Promise<Job> {
  const response = await fetch(`${API_BASE}/api/jobs/${id}/flag`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ flagged }),
  });
  return handleResponse<Job>(response);
}

export async function deleteJob(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/api/jobs/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    const text = await response.text();
    throw new ApiError(response.status, text || response.statusText);
  }
}

export function getExportUrl(filters?: {
  company?: string;
  flagged?: boolean;
}): string {
  const params = new URLSearchParams();
  if (filters?.company) params.set("company", filters.company);
  if (filters?.flagged !== undefined)
    params.set("flagged", filters.flagged.toString());
  const query = params.toString();
  return `${API_BASE}/api/jobs/export${query ? `?${query}` : ""}`;
}
