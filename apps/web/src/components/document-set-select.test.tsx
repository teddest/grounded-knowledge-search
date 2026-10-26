import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { DocumentSetSelect } from "@/components/document-set-select";

const sets = [
  { id: "one", name: "Policies", root_path: "policies", status: "ready" },
  { id: "two", name: "Procedures", root_path: "procedures", status: "ready" },
];

describe("DocumentSetSelect", () => {
  it("opens, selects an option, and closes", async () => {
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

    await user.click(screen.getByRole("button", { name: "Policies (ready)" }));
    expect(screen.getByRole("listbox")).toBeVisible();
    await user.click(screen.getByRole("option", { name: /Procedures/ }));

    expect(onChange).toHaveBeenCalledWith("two");
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("supports keyboard navigation and escape", () => {
    const onChange = vi.fn();
    const { rerender } = render(
      <DocumentSetSelect
        id="documents"
        documentSets={sets}
        selectedId="one"
        disabled={false}
        onChange={onChange}
      />,
    );
    const button = screen.getByRole("button", { name: "Policies (ready)" });

    fireEvent.keyDown(button, { key: "a" });
    fireEvent.keyDown(button, { key: "ArrowDown" });
    expect(screen.getByRole("listbox")).toBeVisible();
    fireEvent.keyDown(button, { key: "ArrowDown" });
    expect(onChange).toHaveBeenCalledWith("two");
    rerender(
      <DocumentSetSelect
        id="documents"
        documentSets={sets}
        selectedId="two"
        disabled={false}
        onChange={onChange}
      />,
    );
    const selectedButton = screen.getByRole("button", { name: "Procedures (ready)" });
    fireEvent.keyDown(selectedButton, { key: "Escape" });
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();

    fireEvent.keyDown(selectedButton, { key: "Enter" });
    expect(screen.getByRole("listbox")).toBeVisible();
    fireEvent.keyDown(selectedButton, { key: " " });
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
    fireEvent.keyDown(selectedButton, { key: "Enter" });
    fireEvent.keyDown(selectedButton, { key: "ArrowUp" });
    expect(onChange).toHaveBeenCalledWith("one");
  });

  it("handles empty and disabled states", () => {
    render(
      <DocumentSetSelect
        id="documents"
        documentSets={[]}
        selectedId=""
        disabled={false}
        onChange={() => undefined}
      />,
    );
    const emptyButton = screen.getByRole("button", { name: "Select a document set" });
    fireEvent.click(emptyButton);
    expect(screen.getByText("No document sets available.")).toBeVisible();
    fireEvent.keyDown(emptyButton, { key: "ArrowDown" });
    fireEvent.keyDown(emptyButton, { key: "Escape" });

    render(
      <DocumentSetSelect
        id="disabled"
        documentSets={sets}
        selectedId="one"
        disabled
        onChange={() => undefined}
      />,
    );
    expect(screen.getByRole("button", { name: "Policies (ready)" })).toBeDisabled();
  });
});
