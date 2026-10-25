import type { paths } from "@grounded/contracts";

export type ApiHealth =
  paths["/health"]["get"]["responses"][200]["content"]["application/json"];

export type ApiFetcher = typeof fetch;

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export function apiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
}

export async function fetchHealth(fetcher: ApiFetcher = fetch): Promise<ApiHealth> {
  const response = await fetcher(`${apiBaseUrl()}/health`, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new ApiError("The API health check failed.", response.status);
  }

  return (await response.json()) as ApiHealth;
}
