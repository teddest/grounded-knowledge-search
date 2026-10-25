import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ServiceStatus } from "@/components/service-status";

const fetchHealth = vi.hoisted(() => vi.fn());

vi.mock("@/lib/api", () => ({ fetchHealth }));

describe("ServiceStatus", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("shows a checking state before the health request resolves", () => {
    fetchHealth.mockReturnValue(new Promise(() => undefined));

    render(<ServiceStatus />);

    expect(screen.getByRole("status")).toHaveTextContent("Checking API and database status");
  });

  it("shows the ready state after a successful health request", async () => {
    fetchHealth.mockResolvedValue({ status: "ok", database: "ok" });

    render(<ServiceStatus />);

    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("ready"));
  });

  it("shows an API error message when the health request fails", async () => {
    fetchHealth.mockRejectedValue(new Error("The API health check failed."));

    render(<ServiceStatus />);

    expect(await screen.findByRole("alert")).toHaveTextContent("The API health check failed.");
  });

  it("uses a safe message for non-Error failures", async () => {
    fetchHealth.mockRejectedValue("network failure");

    render(<ServiceStatus />);

    expect(await screen.findByRole("alert")).toHaveTextContent("The API is unavailable.");
  });

  it("ignores a successful response after unmount", async () => {
    let resolveRequest: (value: unknown) => void = () => undefined;
    fetchHealth.mockReturnValue(
      new Promise((resolve) => {
        resolveRequest = resolve;
      }),
    );

    const { unmount } = render(<ServiceStatus />);
    unmount();
    resolveRequest({ status: "ok", database: "ok" });
    await Promise.resolve();

    expect(screen.queryByText("API and database are ready.")).not.toBeInTheDocument();
  });

  it("ignores a failed response after unmount", async () => {
    let rejectRequest: (reason: unknown) => void = () => undefined;
    fetchHealth.mockReturnValue(
      new Promise((_resolve, reject) => {
        rejectRequest = reject;
      }),
    );

    const { unmount } = render(<ServiceStatus />);
    unmount();
    rejectRequest(new Error("late failure"));
    await Promise.resolve();

    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
