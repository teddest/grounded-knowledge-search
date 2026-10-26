import { afterEach, describe, expect, it, vi } from "vitest";

const openApiClient = vi.hoisted(() => ({
  GET: vi.fn(),
  POST: vi.fn(),
}));

vi.mock("openapi-fetch", () => ({
  default: () => openApiClient,
}));

import {
  ApiError,
  apiBaseUrl,
  askGroundedQuestion,
  createDocumentSet,
  discoverDocumentSets,
  fetchHealth,
  indexDocumentSet,
  ingestDocumentSet,
  listDocumentSets,
  searchDocuments,
} from "@/lib/api";

describe("api", () => {
  afterEach(() => {
    vi.clearAllMocks();
    vi.unstubAllGlobals();
  });

  it("uses the default API base URL", () => {
    expect(apiBaseUrl()).toBe("http://localhost:8000");
  });

  it("uses the configured API base URL when provided", () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://api:8000");
    expect(apiBaseUrl()).toBe("http://api:8000");
    vi.unstubAllEnvs();
  });

  it("returns a healthy API response", async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(JSON.stringify({ status: "ok", database: "ok" }), { status: 200 }),
    );

    await expect(fetchHealth(fetcher)).resolves.toEqual({ status: "ok", database: "ok" });
    expect(fetcher).toHaveBeenCalledWith("http://localhost:8000/health", {
      headers: { Accept: "application/json" },
    });
  });

  it("throws an ApiError for an unhealthy response", async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(new Response(null, { status: 503 }));

    await expect(fetchHealth(fetcher)).rejects.toEqual(
      new ApiError("The API health check failed.", 503),
    );
  });

  it("discovers document sets", async () => {
    openApiClient.POST.mockResolvedValue({
      data: [{ id: "all", name: "All documents", root_path: "documents", status: "ready" }],
    });

    await expect(discoverDocumentSets()).resolves.toHaveLength(1);
  });

  it("creates a document set", async () => {
    openApiClient.POST.mockResolvedValue({
      data: { id: "all", name: "All documents", root_path: ".", status: "registered" },
    });

    await expect(createDocumentSet("All documents", ".")).resolves.toMatchObject({
      name: "All documents",
      root_path: ".",
    });
  });

  it("calls the typed document-set and ingestion endpoints", async () => {
    openApiClient.GET.mockResolvedValue({
      data: [{ id: "set-1", name: "Policies", root_path: ".", status: "ready" }],
    });
    openApiClient.POST.mockResolvedValue({ data: {} });

    await expect(listDocumentSets()).resolves.toHaveLength(1);
    await expect(ingestDocumentSet("set-1")).resolves.toBeUndefined();
    await expect(indexDocumentSet("set-1")).resolves.toBeUndefined();
    expect(openApiClient.POST).toHaveBeenCalledTimes(2);
  });

  it("calls search and ask endpoints", async () => {
    openApiClient.POST.mockResolvedValue({ data: { query: "refund", results: [] } });
    const filters = { category: null, status: "current", version: null };

    await expect(searchDocuments("set-1", "refund", 5, filters)).resolves.toEqual({
      query: "refund",
      results: [],
    });
    await expect(askGroundedQuestion("set-1", "What is the rule?", 5, filters)).resolves.toEqual({
      query: "refund",
      results: [],
    });
    expect(openApiClient.POST).toHaveBeenCalledTimes(2);
  });

  it("maps endpoint failures to ApiError", async () => {
    openApiClient.GET.mockResolvedValue({ error: { detail: "unavailable" } });
    openApiClient.POST.mockResolvedValue({ error: { detail: "unavailable" } });

    await expect(listDocumentSets()).rejects.toEqual(
      new ApiError("Could not load document sets.", 500),
    );
    await expect(discoverDocumentSets()).rejects.toEqual(
      new ApiError("Could not discover document sets.", 500),
    );
    await expect(createDocumentSet("All documents", ".")).rejects.toEqual(
      new ApiError("Could not create document set.", 500),
    );
    await expect(ingestDocumentSet("set-1")).rejects.toEqual(
      new ApiError("Document ingestion failed.", 500),
    );
    await expect(indexDocumentSet("set-1")).rejects.toEqual(
      new ApiError("Embedding indexing failed.", 500),
    );
    await expect(searchDocuments("set-1", "refund", 5, {})).rejects.toEqual(
      new ApiError("Search failed.", 500),
    );
    await expect(askGroundedQuestion("set-1", "question", 5, {})).rejects.toEqual(
      new ApiError("Grounded answer generation failed.", 500),
    );
  });
});
