import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import HomePage from "@/app/page";

describe("HomePage", () => {
  it("introduces the application and renders service status", () => {
    render(<HomePage />);

    expect(screen.getByRole("heading", { name: "Search documents with evidence." })).toBeVisible();
    expect(screen.getByText(/runtime foundation is ready/i)).toBeVisible();
  });
});
