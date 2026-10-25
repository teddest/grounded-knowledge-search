import { describe, expect, it, vi } from "vitest";

import { ApiError, apiBaseUrl, fetchHealth } from "@/lib/api";

describe("api", () => {
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
});
