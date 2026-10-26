import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { SourceReferenceDialog } from "@/components/source-reference-dialog";
import type { SearchResult } from "@/lib/api";

const source: SearchResult = {
  id: 4,
  source_path: "refunds-2025.md",
  title: "Refund Policy",
  status: "current",
  version: "2025.1",
  heading_path: ["Refunds", "Annual plans"],
  start_line: 13,
  end_line: 17,
  content: "Annual subscriptions have a **30-day** refund window.\nThe rule is current.",
  fusion_score: 0.03,
};

describe("SourceReferenceDialog", () => {
  it("shows formatted content with a line-number gutter", () => {
    render(<SourceReferenceDialog source={source} open onOpenChange={vi.fn()} />);

    expect(screen.getByRole("dialog")).toBeVisible();
    expect(screen.getByRole("heading", { name: "Refund Policy" })).toBeVisible();
    expect(screen.getByText("refunds-2025.md:13-17")).toBeVisible();
    expect(screen.getByRole("dialog")).toHaveTextContent("Annual subscriptions");
    expect(screen.getByText("Annual plans")).toBeVisible();
    expect(screen.getByText("Source lines 13–17")).toBeVisible();
  });

  it("renders fallback metadata and unknown line numbers", () => {
    render(
      <SourceReferenceDialog
        source={{ ...source, status: null, version: null, heading_path: [], start_line: null, end_line: null, content: "" }}
        open
        onOpenChange={vi.fn()}
      />,
    );

    expect(screen.getByText("refunds-2025.md:?-?")).toBeVisible();
    expect(screen.getByText("unknown status")).toBeVisible();
    expect(screen.getByText("unversioned")).toBeVisible();
    expect(screen.getByRole("dialog")).toHaveTextContent("?");
  });

  it("closes through the dialog close control", async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();
    render(<SourceReferenceDialog source={source} open onOpenChange={onOpenChange} />);

    await user.click(screen.getByRole("button", { name: "Close" }));

    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it("renders safely when no source is selected", () => {
    render(<SourceReferenceDialog source={null} open={false} onOpenChange={vi.fn()} />);

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
