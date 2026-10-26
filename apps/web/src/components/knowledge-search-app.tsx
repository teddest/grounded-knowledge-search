"use client";

import Link from "next/link";
import { Info } from "lucide-react";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Streamdown } from "streamdown";

import {
  ApiError,
  askGroundedQuestion,
  createDocumentSet,
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
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

type BusyState = "loading" | "indexing" | "searching" | "answering" | null;
type NoticeKind = "success" | "info";
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
  const [noticeKind, setNoticeKind] = useState<NoticeKind>("success");

  const selectedDocumentSet = useMemo(
    () => documentSets.find((documentSet) => documentSet.id === selectedId),
    [documentSets, selectedId],
  );

  const loadDocumentSets = useCallback(async () => {
    const existingDocumentSets = await listDocumentSets();
    const allDocuments = existingDocumentSets.find(
      (documentSet) => documentSet.root_path === "documents",
    );
    const nextDocumentSets = allDocuments
      ? existingDocumentSets
      : [await createDocumentSet("All documents", "documents"), ...existingDocumentSets];
    setDocumentSets(nextDocumentSets);
    setSelectedId((current) => current || nextDocumentSets[0].id);
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
      setNoticeKind("success");
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
      if (response.results.length === 0) {
        setNotice("No supporting sections were found.");
        setNoticeKind("info");
      }
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
      <header className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
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
        </div>
        <div className="flex flex-col items-end gap-3 lg:self-center">
          <Button size="lg" className="shadow-sm" asChild>
            <Link href="/about">
              <Info />
              About this app
            </Link>
          </Button>
          <ServiceStatus />
        </div>
      </header>

      <Card className="border-slate-200 shadow-sm">
        <CardContent className="p-6">
          <h2 className="font-semibold text-slate-950">Document set</h2>
        <div className="mt-4 flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div className="min-w-0 flex-1">
            <Label htmlFor="document-set">Indexed documents</Label>
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
            <Button type="button" onClick={handleIndexing} disabled={busy !== null}>
              {busy === "indexing" ? "Analyzing…" : "Analyze and index"}
            </Button>
          </div>
          </div>
        </CardContent>
      </Card>

      {(error || notice) && (
        <Alert
          className={`mt-6 ${
            error
              ? ""
              : noticeKind === "success"
                ? "border-emerald-200 bg-emerald-50 text-emerald-900"
                : "border-amber-200 bg-amber-50 text-amber-950"
          }`}
          variant={error ? "destructive" : "default"}
        >
          <AlertDescription className="flex items-center justify-between gap-4">
            <span>{error || notice}</span>
            {notice && !error && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                aria-label="Dismiss notification"
                onClick={() => {
                  setNotice("");
                  setNoticeKind("success");
                }}
              >
                Dismiss
              </Button>
            )}
          </AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="search" className="mt-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="search">Search evidence</TabsTrigger>
          <TabsTrigger value="ask">Ask a grounded question</TabsTrigger>
        </TabsList>

        <TabsContent value="search" className="space-y-6">
          <Card className="border-slate-200 shadow-sm">
            <CardHeader>
              <h2 className="text-xl font-semibold text-slate-950">Search evidence</h2>
            </CardHeader>
            <CardContent>
              <form className="space-y-4" onSubmit={handleSearch}>
                <Label htmlFor="search-query">Search query</Label>
                <div className="flex gap-3">
                  <Input
                    id="search-query"
                    className="min-w-0 flex-1"
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    placeholder="What is the annual refund window?"
                  />
                  <Button variant="secondary" disabled={busy !== null} type="submit">
                    {busy === "searching" ? "Searching…" : "Search"}
                  </Button>
                </div>
                <FilterControls filters={filters} setFilters={setFilters} />
              </form>
            </CardContent>
          </Card>

          {results.length > 0 ? (
            <section aria-label="Search results" className="space-y-3">
              <div className="flex items-baseline justify-between">
                <h2 className="text-xl font-semibold text-slate-950">Ranked evidence</h2>
                <span className="text-sm text-muted-foreground">{results.length} results</span>
              </div>
              {results.map((result, index) => (
                <ResultCard key={result.id} result={result} rank={index + 1} />
              ))}
            </section>
          ) : (
            <p className="text-sm text-muted-foreground">Search to see ranked evidence.</p>
          )}
        </TabsContent>

        <TabsContent value="ask">
          <Card className="border-slate-200 shadow-sm">
            <CardHeader>
              <h2 className="text-xl font-semibold text-slate-950">Ask a grounded question</h2>
            </CardHeader>
            <CardContent>
              <form className="space-y-4" onSubmit={handleAsk}>
                <Label htmlFor="question">Question</Label>
                <div className="flex gap-3">
                  <Input
                    id="question"
                    className="min-w-0 flex-1"
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                    placeholder="What should Support do after a failed payment?"
                  />
                  <Button disabled={busy !== null} type="submit">
                    {busy === "answering" ? "Answering…" : "Ask"}
                  </Button>
                </div>
              </form>
              {answer ? (
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
              ) : (
                <p className="mt-6 text-sm text-muted-foreground">
                  Ask a question to receive a cited answer grounded in the retrieved documents.
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
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
          <Input
            key={filter}
            aria-label={filter}
            placeholder={filter}
            value={filters[filter]}
            onChange={(event) => setFilters({ ...filters, [filter]: event.target.value })}
          />
        ))}
      </div>
    </fieldset>
  );
}
