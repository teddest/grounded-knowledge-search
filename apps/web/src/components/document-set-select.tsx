"use client";

import { KeyboardEvent, useState } from "react";

import type { DocumentSet } from "@/lib/api";

type DocumentSetSelectProps = {
  id: string;
  documentSets: DocumentSet[];
  selectedId: string;
  disabled: boolean;
  onChange: (documentSetId: string) => void;
};

export function DocumentSetSelect({
  id,
  documentSets,
  selectedId,
  disabled,
  onChange,
}: DocumentSetSelectProps): React.JSX.Element {
  const [open, setOpen] = useState(false);
  const selected = documentSets.find((documentSet) => documentSet.id === selectedId);

  function selectDocumentSet(documentSetId: string): void {
    onChange(documentSetId);
    setOpen(false);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLButtonElement>): void {
    const currentIndex = documentSets.findIndex((documentSet) => documentSet.id === selectedId);
    if (event.key === "Escape") {
      setOpen(false);
      return;
    }
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      setOpen((current) => !current);
      return;
    }
    if (event.key !== "ArrowDown" && event.key !== "ArrowUp") return;
    event.preventDefault();
    if (!open) {
      setOpen(true);
      return;
    }
    if (documentSets.length === 0) return;
    const direction = event.key === "ArrowDown" ? 1 : -1;
    const nextIndex = (currentIndex + direction + documentSets.length) % documentSets.length;
    selectDocumentSet(documentSets[nextIndex].id);
  }

  return (
    <div className="relative">
      <button
        id={id}
        type="button"
        className="flex w-full items-center justify-between rounded-lg border border-slate-300 bg-white px-3 py-2 text-left text-sm text-slate-900 shadow-sm outline-none transition focus:border-sky-600 focus:ring-2 focus:ring-sky-200 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:opacity-60"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={`${id}-options`}
        disabled={disabled}
        onClick={() => setOpen((current) => !current)}
        onKeyDown={handleKeyDown}
      >
        <span>{selected ? `${selected.name} (${selected.status})` : "Select a document set"}</span>
        <span aria-hidden="true" className={`ml-3 transition ${open ? "rotate-180" : ""}`}>
         ⌄
        </span>
      </button>
      {open && (
        <div
          id={`${id}-options`}
          role="listbox"
          aria-label="Document sets"
          className="absolute z-30 mt-2 max-h-64 w-full overflow-auto rounded-lg border border-slate-200 bg-white p-1 shadow-xl"
        >
          {documentSets.length === 0 ? (
            <p className="px-3 py-2 text-sm text-slate-500">No document sets available.</p>
          ) : (
            documentSets.map((documentSet) => (
              <button
                key={documentSet.id}
                type="button"
                role="option"
                aria-selected={documentSet.id === selectedId}
                className={`block w-full rounded-md px-3 py-2 text-left text-sm transition hover:bg-sky-50 ${
                  documentSet.id === selectedId
                    ? "bg-sky-100 font-semibold text-sky-900"
                    : "text-slate-700"
                }`}
                onClick={() => selectDocumentSet(documentSet.id)}
              >
                <span>{documentSet.name}</span>
                <span className="ml-2 text-xs text-slate-500">{documentSet.status}</span>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
