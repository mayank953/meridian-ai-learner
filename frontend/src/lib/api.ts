/**
 * api.ts — Centralized API client for the FastAPI backend.
 */

const BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? "http://localhost:8080" : "");

async function request<T = unknown>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, options);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// ─── RAG ─────────────────────────────────────────────────────

export async function uploadDocument(file: File) {
  const form = new FormData();
  form.append("files", file);
  return request<{ results: Array<{ filename: string; status: string; reason?: string; pages?: number; chunks?: number }> }>("/api/rag/upload", { method: "POST", body: form });
}

export async function uploadDocuments(files: File[]) {
  const form = new FormData();
  for (const file of files) {
    form.append("files", file);
  }
  return request<{ results: Array<{ filename: string; status: string; reason?: string; pages?: number; chunks?: number }> }>("/api/rag/upload", { method: "POST", body: form });
}

export async function listUploads() {
  return request("/api/rag/uploads");
}

export async function askQuestion(query: string, retrieverType: string = "similarity") {
  return request<{ answer: string }>("/api/rag/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, retriever_type: retrieverType }),
  });
}

export async function triggerGcsIngestion() {
  return request<{ status: string }>("/api/rag/ingest-gcs", { method: "POST" });
}

// ─── Agent ───────────────────────────────────────────────────

export async function runAudit(requestText: string) {
  return request<{
    risk_result: string;
    tax_result: string;
    control_result: string;
    cfo_memo: string;
  }>("/api/agent/audit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ request_text: requestText }),
  });
}

// ─── Health ──────────────────────────────────────────────────

export async function healthCheck() {
  return request("/api/health");
}

export interface SystemStatus {
  backend?: { status: string; uptime: string; python_version: string; platform: string };
  gcp?: { project_id: string; region: string };
  storage?: { gcs_bucket: string; gcs_prefix: string };
  vector_search?: { index_id: string; endpoint_id: string; stream_update: boolean };
  models?: { embedding: string; llm: string; llm_framework: string };
  ingestion?: { uploads_this_session: number };
}

export async function getSystemStatus() {
  return request<SystemStatus>("/api/status");
}
