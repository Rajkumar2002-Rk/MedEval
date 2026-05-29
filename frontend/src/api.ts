import type { TriageRequest, TriageResponse } from "./types";

const API_KEY_STORAGE_KEY = "medeval_api_key";

export function getApiKey(): string | null {
  return localStorage.getItem(API_KEY_STORAGE_KEY);
}

export function setApiKey(key: string): void {
  localStorage.setItem(API_KEY_STORAGE_KEY, key);
}

export function clearApiKey(): void {
  localStorage.removeItem(API_KEY_STORAGE_KEY);
}

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export async function triage(
  request: TriageRequest
): Promise<TriageResponse> {
  const apiKey = getApiKey();
  if (!apiKey) {
    throw new ApiError(401, "API key not set. Please configure it in Settings.");
  }

  const response = await fetch(`${API_BASE_URL}/triage`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": apiKey,
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    // Try to extract the backend's detail message; fall back to generic.
    let detail = `Request failed with status ${response.status}`;
    try {
      const errorBody = await response.json();
      if (errorBody?.detail) detail = errorBody.detail;
    } catch {
      // Body wasn't JSON — keep the generic message.
    }
    throw new ApiError(response.status, detail);
  }

  return (await response.json()) as TriageResponse;
}