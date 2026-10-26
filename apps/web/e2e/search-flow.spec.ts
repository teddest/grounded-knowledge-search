import { test, expect } from "@playwright/test";

test("searches evidence and asks a cited question", async ({ page }) => {
  await page.route("**/health", async (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "ok", database: "ok" }) }),
  );
  await page.route("**/api/v1/document-sets**", async (route) => {
    const pathname = new URL(route.request().url()).pathname;
    if (pathname.endsWith("/discover")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          { id: "set-1", name: "Policies", root_path: "policies", status: "ready" },
        ]),
      });
      return;
    }
    if (route.request().method() === "POST") {
      await route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify({ id: "all-set", name: "All documents", root_path: "documents", status: "ready" }),
      });
      return;
    }
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
  });
  await page.route("**/api/v1/search*", async (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        query: "refund",
        results: [
          {
            id: 1,
            source_path: "refunds-2025.md",
            title: "Refund Policy",
            category: "billing",
            status: "current",
            version: "2025.1",
            heading_path: ["Standard refund window"],
            start_line: 1,
            end_line: 4,
            content: "Annual subscriptions have a 30-day refund window.",
            similarity: 0.9,
            lexical_score: 1,
            vector_rank: 1,
            lexical_rank: 1,
            fusion_score: 0.03,
          },
        ],
      }),
    }),
  );
  await page.route("**/api/v1/ask*", async (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        answer: "Annual subscriptions have a **30-day** refund window [1].",
        sources: [
          {
            id: 1,
            source_path: "refunds-2025.md",
            title: "Refund Policy",
            status: "current",
            version: "2025.1",
            heading_path: ["Standard refund window"],
            start_line: 1,
            end_line: 4,
            content: "Annual subscriptions have a 30-day refund window.",
            fusion_score: 0.03,
          },
        ],
      }),
    }),
  );

  await page.goto("/");
  await expect(page.getByText("API and database are ready.")).toBeVisible();
  await page.getByLabel("Search query").fill("What is the refund window?");
  await page.getByRole("button", { name: "Search" }).click();
  await expect(page.getByRole("region", { name: "Search results" })).toBeVisible();
  await expect(page.getByRole("heading", { name: /Refund Policy/ })).toBeVisible();
  await expect(page.getByText("refunds-2025.md:1-4")).toBeVisible();

  await page.getByRole("tab", { name: "Ask a grounded question" }).click();
  await page.getByRole("textbox", { name: "Question" }).fill("What is the refund rule?");
  await page.getByRole("button", { name: "Ask" }).click();
  const renderedAnswer = page.getByText(/refund window \[1\]/);
  await expect(renderedAnswer).toBeVisible();
  await expect(renderedAnswer).not.toContainText("**");
  await expect(page.getByText("[1] refunds-2025.md:1-4")).toBeVisible();
});
