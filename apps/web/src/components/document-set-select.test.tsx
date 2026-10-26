import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { DocumentSetSelect } from "@/components/document-set-select";

const sets = [
  { id: "one", name: "Policies", root_path: "policies", status: "ready" },
  { id: "two", name: "Procedures", root_path: "procedures", status: "ready" },
];

describe("DocumentSetSelect", () => {
  it("opens and selects a document set through the shadcn select", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(
      <DocumentSetSelect
        id="documents"
        documentSets={sets}
        selectedId="one"
        disabled={false}
        onChange={onChange}
      />,
    );

    await user.click(screen.getByRole("combobox", { name: "Indexed documents" }));
    await user.click(screen.getByRole("option", { name: "Procedures (ready)" }));

    expect(onChange).toHaveBeenCalledWith("two");
  });

  it("renders empty and disabled states", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(
      <DocumentSetSelect
        id="empty"
        documentSets={[]}
        selectedId=""
        disabled={false}
        onChange={onChange}
      />,
    );
    await user.click(screen.getByRole("combobox", { name: "Indexed documents" }));
    expect(screen.getByText("No document sets available.")).toBeVisible();

    const disabledView = render(
      <DocumentSetSelect
        id="disabled"
        documentSets={sets}
        selectedId="one"
        disabled
        onChange={onChange}
      />,
    );
    expect(disabledView.getByRole("combobox", { name: "Indexed documents" })).toBeDisabled();
  });
});
