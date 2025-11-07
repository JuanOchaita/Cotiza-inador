export const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

type ApiMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export interface ApiRequestOptions extends RequestInit {
  token?: string | null;
  method?: ApiMethod;
  body?: BodyInit | Record<string, unknown> | null;
}

export class ApiError extends Error {
  public status: number;
  public details?: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

export async function apiRequest<T>(
  endpoint: string,
  { token, headers = {}, method = "GET", body = null, ...rest }: ApiRequestOptions = {},
): Promise<T> {
  const url = endpoint.startsWith("http") ? endpoint : `${API_BASE_URL}${endpoint}`;
  const finalHeaders = new Headers(headers);

  if (token) {
    finalHeaders.set("Authorization", `Bearer ${token}`);
  }

  let finalBody = body;
  if (body && typeof body === "object" && !(body instanceof FormData) && !(body instanceof Blob)) {
    finalHeaders.set("Content-Type", "application/json");
    finalBody = JSON.stringify(body);
  }

  const response = await fetch(url, {
    method,
    body: finalBody as BodyInit | null,
    headers: finalHeaders,
    ...rest,
  });

  const isJson = response.headers.get("content-type")?.includes("application/json");
  const payload = isJson ? await response.json() : null;

  if (!response.ok) {
    const message = (payload?.detail as string) ?? response.statusText ?? "Request failed";
    throw new ApiError(message, response.status, payload);
  }

  return payload as T;
}
