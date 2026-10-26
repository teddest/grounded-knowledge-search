"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Streamdown } from "streamdown";

import {
  ApiError,
  askGroundedQuestion,
  DocumentSet,
  GroundedAnswer,
  indexDocumentSet,
  ingestDocumentSet,
  listDocumentSets,
  SearchFilters,
  SearchResult,
  searchDocuments,
} from "@/lib/api";

import { DocumentSetSelect } from "@/components/document-set-select";
import { ResultCard } from "@/components/result-card";
import { ServiceStatus } from "@/components/service-status";

type BusyState = "loading" | "indexing" | "searching" | "answering" | null;
type FilterState = { category: string; status: string; version: string };

const emptyFilters: FilterState = { category: "", status: "", version: "" };

function errorMessage(error: unknown, fallback: string): string {
  return error instanceof ApiError || error instanceof Error ? error.message : fallback;
}

export function KnowledgeSearchApp(): React.JSX.Element {
  const [documentSets, setDocumentSets] = useState<DocumentSet[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [query, setQuery] = useState("");
  const [question, setQuestion] = useState("");
  const [filters, setFilters] = useState<FilterState>(emptyFilters);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [answer, setAnswer] = useState<GroundedAnswer | null>(null);
  const [busy, setBusy] = useState<BusyState>("loading");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const selectedDocumentSet = useMemo(
    () => documentSets.find((documentSet) => documentSet.id === selectedId),
    [documentSets, selectedId],
  );

  const loadDocumentSets = useCallback(async () => {
    const nextDocumentSets = await listDocumentSets();
    setDocumentSets(nextDocumentSets);
    setSelectedId((current) => current || nextDocumentSets[0]?.id || "");
  }, []);

  useEffect(() => {
    // Initial remote data load is the synchronization boundary for this screen.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadDocumentSets()
      .catch((loadError: unknown) => setError(errorMessage(loadError, "Could not load document sets.")))
      .finally(() => setBusy(null));
  }, [loadDocumentSets]);

  function requestFilters(): SearchFilters {
    return {
      category: filters.category || null,
      status: filters.status || null,
      version: filters.version || null,
    };
  }

  async function handleIndexing(): Promise<void> {
    if (!selectedId) {
      setError("Select a document set first.");
      return;
    }
    setBusy("indexing");
    setError("");
    setNotice("");
    try {
      await ingestDocumentSet(selectedId);
      await indexDocumentSet(selectedId);
      await loadDocumentSets();
      setNotice("Documents analyzed and embeddings indexed.");
    } catch (indexError: unknown) {
      setError(errorMessage(indexError, "Document indexing failed."));
    } finally {
      setBusy(null);
    }
  }

  async function handleSearch(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!selectedId) {
      setError("Select a document set first.");
      return;
    }
    if (!query.trim()) {
      setError("Enter a search query.");
      return;
    }
    setBusy("searching");
    setError("");
    setNotice("");
    setAnswer(null);
    try {
      const response = await searchDocuments(selectedId, query, 8, requestFilters());
      setResults(response.results);
      if (response.results.length === 0) setNotice("No supporting sections were found.");
    } catch (searchError: unknown) {
      setError(errorMessage(searchError, "Search failed."));
    } finally {
      setBusy(null);
    }
  }

  async function handleAsk(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!selectedId) {
      setError("Select a document set first.");
      return;
    }
    if (!question.trim()) {
      setError("Enter a question.");
      return;
    }
    setBusy("answering");
    setError("");
    setNotice("");
    try {
      setAnswer(await askGroundedQuestion(selectedId, question, 8, requestFilters()));
    } catch (answerError: unknown) {
      setError(errorMessage(answerError, "Grounded answer generation failed."));
    } finally {
      setBusy(null);
    }
  }

  return (
    <main className="mx-auto min-h-screen max-w-6xl px-6 py-10">
      <header className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-wide text-sky-700">
          Grounded Knowledge Search
        </p>
        <h1 className="mt-3 text-4xl font-bold tracking-tight text-slate-950">
          Find evidence. Understand the answer.
        </h1>
        <p className="mt-3 max-w-3xl text-lg text-slate-600">
          Explore document sections with hybrid retrieval, then ask questions grounded in the
          sources returned by search.
        </p>
      </header>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="min-w-0 flex-1">
            <h2 className="font-semibold text-slate-950">Document set</h2>
            <label className="mt-4 block text-sm font-medium text-slate-700" htmlFor="document-set">
              Indexed documents
            </label>
            <div className="mt-2 max-w-xl">
              <DocumentSetSelect
                id="document-set"
                documentSets={documentSets}
                selectedId={selectedId}
                disabled={busy === "loading"}
                onChange={setSelectedId}
              />
            </div>
            {selectedDocumentSet && (
              <p className="mt-3 break-words text-xs text-slate-500">
                {selectedDocumentSet.root_path} · {selectedDocumentSet.status}
              </p>
            )}
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <div className="rounded-lg border border-slate-200 px-4 py-2">
              <ServiceStatus />
            </div>
            <button
              type="button"
              className="rounded-lg bg-sky-700 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-800 disabled:cursor-not-allowed disabled:opacity-50"
              onClick={handleIndexing}
              disabled={busy !== null}
            >
              {busy === "indexing" ? "Analyzing…" : "Analyze and index"}
            </button>
          </div>
        </div>
      </section>

      {(error || notice) && (
        <div
          className={`mt-6 rounded-lg border px-4 py-3 text-sm ${
            error
              ? "border-red-200 bg-red-50 text-red-800"
              : "border-emerald-200 bg-emerald-50 text-emerald-800"
          }`}
          role={error ? "alert" : "status"}
        >
          {error || notice}
        </div>
      )}

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-950">Search evidence</h2>
          <form className="mt-4 space-y-4" onSubmit={handleSearch}>
            <label className="block text-sm font-medium text-slate-700" htmlFor="search-query">
              Search query
            </label>
            <div className="flex gap-3">
              <input
                id="search-query"
                className="min-w-0 flex-1 rounded-lg border border-slate-300 px-3 py-2"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="What is the annual refund window?"
              />
              <button
                className="rounded-lg bg-slate-900 px-4 py-2 font-semibold text-white disabled:opacity-50"
                disabled={busy !== null}
                type="submit"
              >
                {busy === "searching" ? "Searching…" : "Search"}
              </button>
            </div>
            <FilterControls filters={filters} setFilters={setFilters} />
          </form>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-950">Ask a grounded question</h2>
          <form className="mt-4 space-y-4" onSubmit={handleAsk}>
            <label className="block text-sm font-medium text-slate-700" htmlFor="question">
              Question
            </label>
            <div className="flex gap-3">
              <input
                id="question"
                className="min-w-0 flex-1 rounded-lg border border-slate-300 px-3 py-2"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="What should Support do after a failed payment?"
              />
              <button
                className="rounded-lg bg-sky-700 px-4 py-2 font-semibold text-white disabled:opacity-50"
                disabled={busy !== null}
                type="submit"
              >
                {busy === "answering" ? "Answering…" : "Ask"}
              </button>
            </div>
          </form>
          {answer && (
            <div className="mt-6 rounded-xl bg-slate-50 p-5">
              <h3 className="font-semibold text-slate-950">Answer</h3>
              <Streamdown mode="static" className="mt-3 text-slate-800">
                {answer.answer}
              </Streamdown>
              <h3 className="mt-5 font-semibold text-slate-950">Sources</h3>
              <ul className="mt-2 space-y-2 text-sm text-sky-800">
                {answer.sources.map((source, index) => (
                  <li key={source.id}>
                    [{index + 1}] {source.source_path}:{source.start_line ?? "?"}-
                    {source.end_line ?? "?"}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      </div>

      {results.length > 0 && (
        <section aria-label="Search results" className="mt-6 space-y-3">
          <h2 className="text-xl font-semibold text-slate-950">Ranked evidence</h2>
          {results.map((result, index) => (
            <ResultCard key={result.id} result={result} rank={index + 1} />
          ))}
        </section>
      )}
    </main>
  );
}

function FilterControls({
  filters,
  setFilters,
}: {
  filters: FilterState;
  setFilters: (filters: FilterState) => void;
}): React.JSX.Element {
  return (
    <fieldset>
      <legend className="text-sm font-medium text-slate-700">Filters</legend>
      <div className="mt-2 grid gap-3 sm:grid-cols-3">
        {(["category", "status", "version"] as const).map((filter) => (
          <input
            key={filter}
            aria-label={filter}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder={filter}
            value={filters[filter]}
            onChange={(event) => setFilters({ ...filters, [filter]: event.target.value })}
          />
        ))}
      </div>
    </fieldset>
  );
}
