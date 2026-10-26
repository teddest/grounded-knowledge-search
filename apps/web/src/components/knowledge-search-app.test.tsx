import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { KnowledgeSearchApp } from "@/components/knowledge-search-app";
import { ApiError } from "@/lib/api";

const api = vi.hoisted(() => ({
  askGroundedQuestion: vi.fn(),
  createDocumentSet: vi.fn(),
  fetchHealth: vi.fn(),
  indexDocumentSet: vi.fn(),
  ingestDocumentSet: vi.fn(),
  listDocumentSets: vi.fn(),
  searchDocuments: vi.fn(),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return { ...actual, ...api };
});

vi.mock("streamdown", () => ({
  Streamdown: ({ children }: { children: string }) => <div data-testid="streamdown">{children}</div>,
}));

const documentSet = {
  id: "set-1",
  name: "Policies",
  root_path: "documents",
  status: "ready",
};

const searchResult = {
  id: 1,
  source_path: "refunds-2025.md",
  title: "Refund Policy",
  category: "billing",
  status: "current",
  version: "2025.1",
  effective_date: "2025-02-01",
  heading_path: ["Standard refund window"],
  start_line: 1,
  end_line: 4,
  content: "Annual subscriptions have a 30-day refund window.",
  similarity: 0.9,
  lexical_score: 1,
  vector_rank: 1,
  lexical_rank: 1,
  fusion_score: 0.03,
};

function searchResponse(results = [searchResult]) {
  return { query: "refund", results };
}

function answerResponse() {
  return {
    answer: "Annual subscriptions have a 30-day window [1].",
    sources: [searchResult],
  };
}

async function renderReady() {
  api.listDocumentSets.mockResolvedValue([documentSet]);
  api.fetchHealth.mockResolvedValue({ status: "ok", database: "ok" });
  render(<KnowledgeSearchApp />);
  await waitFor(() => expect(screen.getByRole("combobox", { name: "Indexed documents" })).toBeVisible());
}

describe("KnowledgeSearchApp", () => {
  beforeEach(() => {
    api.createDocumentSet.mockResolvedValue({
      id: "all-set",
      name: "All documents",
      root_path: "documents",
      status: "registered",
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("loads document sets and shows service status", async () => {
    await renderReady();

    expect(screen.getByText("API and database are ready.")).toBeVisible();
    expect(screen.getByText(/documents · ready/)).toBeVisible();
    expect(screen.getByRole("button", { name: "Analyze and index" })).toBeEnabled();
  });

  it("creates and selects an all-documents set by default", async () => {
    const user = userEvent.setup();
    const policies = { ...documentSet, id: "policies", name: "Policies", root_path: "policies" };
    api.listDocumentSets.mockResolvedValue([policies]);
    api.fetchHealth.mockResolvedValue({ status: "ok", database: "ok" });
    render(<KnowledgeSearchApp />);

    await waitFor(() => expect(screen.getByText("All documents (registered)")).toBeVisible());
    expect(api.createDocumentSet).toHaveBeenCalledWith("All documents", "documents");
    await user.click(screen.getByRole("button", { name: "Analyze and index" }));
    expect(api.ingestDocumentSet).toHaveBeenCalledWith("all-set");
  });

  it("shows loading and unknown-load-error states", async () => {
    let resolve: (value: typeof documentSet[]) => void = () => undefined;
    api.listDocumentSets.mockReturnValue(new Promise((value) => (resolve = value)));
    api.fetchHealth.mockResolvedValue({ status: "ok", database: "ok" });
    render(<KnowledgeSearchApp />);
    expect(screen.getByRole("combobox", { name: "Indexed documents" })).toBeDisabled();
    resolve([documentSet]);
    await waitFor(() => expect(screen.getByRole("combobox", { name: "Indexed documents" })).toBeVisible());

    api.listDocumentSets.mockRejectedValue("network failure");
    render(<KnowledgeSearchApp />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Could not load document sets.");
  });

  it("analyzes and indexes the selected document set", async () => {
    const user = userEvent.setup();
    await renderReady();
    api.ingestDocumentSet.mockResolvedValue(undefined);
    api.indexDocumentSet.mockResolvedValue(undefined);
    api.listDocumentSets.mockResolvedValue([documentSet]);

    await user.click(screen.getByRole("button", { name: "Analyze and index" }));

    await waitFor(() => expect(screen.getByText(/Documents analyzed/)).toBeVisible());
    await user.click(screen.getByRole("button", { name: "Dismiss notification" }));
    expect(screen.queryByText(/Documents analyzed/)).not.toBeInTheDocument();
    expect(api.ingestDocumentSet).toHaveBeenCalledWith("set-1");
    expect(api.indexDocumentSet).toHaveBeenCalledWith("set-1");
  });

  it("shows indexing errors and supports a missing selection", async () => {
    const user = userEvent.setup();
    await renderReady();
    api.ingestDocumentSet.mockRejectedValue(new ApiError("No key", 503));
    await user.click(screen.getByRole("button", { name: "Analyze and index" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("No key");

    cleanup();
    api.listDocumentSets.mockResolvedValue([]);
    api.createDocumentSet.mockRejectedValue(new Error("default set unavailable"));
    render(<KnowledgeSearchApp />);
    await waitFor(() => expect(screen.getByRole("combobox", { name: "Indexed documents" })).toBeVisible());
    await user.click(screen.getByRole("button", { name: "Analyze and index" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Select a document set first.");
  });

  it("searches with filters and renders ranked evidence", async () => {
    const user = userEvent.setup();
    await renderReady();
    api.searchDocuments.mockResolvedValue(searchResponse());

    await user.type(screen.getByLabelText("Search query"), "refund");
    await user.type(screen.getByLabelText("category"), "billing");
    await user.type(screen.getByLabelText("status"), "current");
    await user.type(screen.getByLabelText("version"), "2025.1");
    await user.click(screen.getByRole("button", { name: "Search" }));

    await waitFor(() => expect(screen.getByText("Annual subscriptions have a 30-day refund window.")).toBeVisible());
    expect(api.searchDocuments).toHaveBeenCalledWith("set-1", "refund", 8, {
      category: "billing",
      status: "current",
      version: "2025.1",
    });
  });

  it("handles empty search results and search errors", async () => {
    const user = userEvent.setup();
    await renderReady();
    api.searchDocuments.mockResolvedValue(searchResponse([]));
    await user.type(screen.getByLabelText("Search query"), "unknown");
    await user.click(screen.getByRole("button", { name: "Search" }));
    expect(await screen.findByText(/No supporting sections/)).toBeVisible();

    api.searchDocuments.mockRejectedValue("search outage");
    await user.click(screen.getByRole("button", { name: "Search" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Search failed.");

    await user.clear(screen.getByLabelText("Search query"));
    await user.click(screen.getByRole("button", { name: "Search" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Enter a search query.");
  });

  it("asks a question and renders cited sources", async () => {
    const user = userEvent.setup();
    await renderReady();
    api.askGroundedQuestion.mockResolvedValue(answerResponse());

    await user.click(screen.getByRole("tab", { name: "Ask a grounded question" }));
    await user.type(screen.getByLabelText("Question"), "What is the refund rule?");
    await user.click(screen.getByRole("button", { name: "Ask" }));

    await waitFor(() => expect(screen.getByText(/30-day window/)).toBeVisible());
    expect(screen.getByText("[1] refunds-2025.md:1-4")).toBeVisible();
  });

  it("renders source fallbacks when line ranges are missing", async () => {
    const user = userEvent.setup();
    await renderReady();
    api.askGroundedQuestion.mockResolvedValue({
      answer: "Evidence [1]",
      sources: [{ ...searchResult, start_line: null, end_line: null }],
    });
    await user.click(screen.getByRole("tab", { name: "Ask a grounded question" }));
    await user.type(screen.getByLabelText("Question"), "What is the rule?");
    await user.click(screen.getByRole("button", { name: "Ask" }));
    expect(await screen.findByText("[1] refunds-2025.md:?-?")).toBeVisible();
  });

  it("handles answer errors and empty questions", async () => {
    const user = userEvent.setup();
    await renderReady();
    api.askGroundedQuestion.mockRejectedValue(new Error("model unavailable"));
    await user.click(screen.getByRole("tab", { name: "Ask a grounded question" }));
    await user.type(screen.getByLabelText("Question"), "What is the rule?");
    await user.click(screen.getByRole("button", { name: "Ask" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("model unavailable");

    await user.clear(screen.getByLabelText("Question"));
    await user.click(screen.getByRole("button", { name: "Ask" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Enter a question.");
  });

  it("validates missing selections and supports changing document sets", async () => {
    const user = userEvent.setup();
    const secondSet = { ...documentSet, id: "set-2", name: "Procedures" };
    api.listDocumentSets.mockResolvedValue([documentSet, secondSet]);
    api.fetchHealth.mockResolvedValue({ status: "ok", database: "ok" });
    render(<KnowledgeSearchApp />);
    await waitFor(() => expect(screen.getByRole("combobox", { name: "Indexed documents" })).toBeVisible());
    await user.click(screen.getByRole("combobox", { name: "Indexed documents" }));
    await user.click(screen.getByRole("option", { name: /Procedures/ }));
    expect(screen.getByText("Procedures (ready)")).toBeVisible();

    cleanup();
    api.listDocumentSets.mockResolvedValue([]);
    api.createDocumentSet.mockRejectedValue(new Error("default set unavailable"));
    render(<KnowledgeSearchApp />);
    await waitFor(() => expect(screen.getByRole("combobox", { name: "Indexed documents" })).toBeVisible());
    await user.click(screen.getByRole("button", { name: "Search" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Select a document set first.");
    await user.click(screen.getByRole("tab", { name: "Ask a grounded question" }));
    await user.click(screen.getByRole("button", { name: "Ask" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Select a document set first.");
  });

  it("shows provider status errors", async () => {
    api.listDocumentSets.mockResolvedValue([documentSet]);
    api.fetchHealth.mockRejectedValue(new Error("API is unavailable"));
    render(<KnowledgeSearchApp />);

    expect(await screen.findByRole("alert")).toHaveTextContent("API is unavailable");
  });
});
