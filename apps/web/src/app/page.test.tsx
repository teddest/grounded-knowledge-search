import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import HomePage from "@/app/page";

describe("HomePage", () => {
  it("renders the search application", () => {
    render(<HomePage />);

    expect(screen.getByRole("heading", { name: "Find evidence. Understand the answer." })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Search evidence" })).toBeVisible();
  });
});
