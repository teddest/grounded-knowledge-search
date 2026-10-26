import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import AboutPage from "@/app/about/page";

describe("AboutPage", () => {
  it("explains the system for educational readers", () => {
    render(<AboutPage />);

    expect(screen.getByRole("heading", { name: "About the application" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Retrieval and ranking" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Data handling and limitations" })).toBeVisible();
    expect(screen.getByRole("link", { name: "Back to search" })).toHaveAttribute("href", "/");
  });
});
