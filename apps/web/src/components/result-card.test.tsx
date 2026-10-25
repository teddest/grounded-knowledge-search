import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ResultCard } from "@/components/result-card";
import type { SearchResult } from "@/lib/api";

const baseResult: SearchResult = {
  id: 1,
  source_path: "policies/refunds.md",
  title: "Refund Policy",
  status: "current",
  version: "2025.1",
  heading_path: ["Refunds", "Annual plans"],
  start_line: 10,
  end_line: 20,
  content: "Annual refunds are available.",
  similarity: 0.9,
  lexical_score: 1.2,
  fusion_score: 0.03,
};

describe("ResultCard", () => {
  it("renders source metadata and retrieval diagnostics", () => {
    render(<ResultCard result={baseResult} rank={1} />);

    expect(screen.getByRole("heading", { name: /Refund Policy/ })).toBeVisible();
    expect(screen.getByText("policies/refunds.md:10-20")).toBeVisible();
    expect(screen.getByText(/Refunds > Annual plans/)).toBeVisible();
    expect(screen.getByText("0.0300")).toBeVisible();
    expect(screen.getByText("0.9000")).toBeVisible();
    expect(screen.getByText("1.2000")).toBeVisible();
  });

  it("renders safe fallbacks when optional metadata is absent", () => {
    render(
      <ResultCard
        result={{
          ...baseResult,
          start_line: null,
          end_line: null,
          heading_path: [],
          status: null,
          version: null,
          similarity: null,
          lexical_score: null,
        }}
        rank={2}
      />,
    );

    expect(screen.getByText("policies/refunds.md:?-?")).toBeVisible();
    expect(screen.getByText(/Document · unknown status · unversioned/)).toBeVisible();
    expect(screen.queryByText(/Semantic:/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Lexical:/)).not.toBeInTheDocument();
  });
});
