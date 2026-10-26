import createClient from "openapi-fetch";

import type { components, paths } from "@grounded/contracts";

export type ApiHealth =
  paths["/health"]["get"]["responses"][200]["content"]["application/json"];
export type DocumentSet = components["schemas"]["DocumentSetResponse"];
export type SearchFilters = components["schemas"]["SearchFilters"];
export type SearchResponse = components["schemas"]["SearchResponse"];
export type SearchResult = components["schemas"]["SearchResult"];
export type GroundedAnswer = components["schemas"]["GroundedAnswer"];

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

const client = createClient<paths>({ baseUrl: apiBaseUrl() });

function throwApiError(status: number, fallback: string): never {
  throw new ApiError(fallback, status);
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

export async function listDocumentSets(): Promise<DocumentSet[]> {
  const { data, error } = await client.GET("/api/v1/document-sets");
  if (error || !data) throwApiError(500, "Could not load document sets.");
  return data;
}

export async function discoverDocumentSets(): Promise<DocumentSet[]> {
  const { data, error } = await client.POST("/api/v1/document-sets/discover", {});
  if (error || !data) throwApiError(500, "Could not discover document sets.");
  return data;
}

export async function createDocumentSet(name: string, path: string): Promise<DocumentSet> {
  const { data, error } = await client.POST("/api/v1/document-sets", {
    body: { name, path },
  });
  if (error || !data) throwApiError(500, "Could not create document set.");
  return data;
}

export async function ingestDocumentSet(documentSetId: string): Promise<void> {
  const { error } = await client.POST(
    "/api/v1/document-sets/{document_set_id}/ingest",
    { params: { path: { document_set_id: documentSetId } } },
  );
  if (error) throwApiError(500, "Document ingestion failed.");
}

export async function indexDocumentSet(documentSetId: string): Promise<void> {
  const { error } = await client.POST(
    "/api/v1/document-sets/{document_set_id}/index",
    { params: { path: { document_set_id: documentSetId } } },
  );
  if (error) throwApiError(500, "Embedding indexing failed.");
}

export async function searchDocuments(
  documentSetId: string,
  query: string,
  limit: number,
  filters: SearchFilters,
): Promise<SearchResponse> {
  const { data, error } = await client.POST("/api/v1/search", {
    body: { document_set_id: documentSetId, query, limit, filters },
  });
  if (error || !data) throwApiError(500, "Search failed.");
  return data;
}

export async function askGroundedQuestion(
  documentSetId: string,
  question: string,
  limit: number,
  filters: SearchFilters,
): Promise<GroundedAnswer> {
  const { data, error } = await client.POST("/api/v1/ask", {
    body: { document_set_id: documentSetId, question, limit, filters },
  });
  if (error || !data) throwApiError(500, "Grounded answer generation failed.");
  return data;
}
