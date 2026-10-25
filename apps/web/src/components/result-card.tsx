import type { SearchResult } from "@/lib/api";

type ResultCardProps = {
  result: SearchResult;
  rank: number;
};

export function ResultCard({ result, rank }: ResultCardProps): React.JSX.Element {
  const location = `${result.source_path}:${result.start_line ?? "?"}-${result.end_line ?? "?"}`;
  const heading = result.heading_path?.join(" > ") || "Document";

  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="font-semibold text-slate-950">
          <span className="mr-2 text-sky-700">#{rank}</span>
          {result.title}
        </h3>
        <code className="text-xs text-slate-500">{location}</code>
      </div>
      <p className="mt-2 text-sm text-slate-600">
        {heading} · {result.status ?? "unknown status"} · {result.version ?? "unversioned"}
      </p>
      <p className="mt-4 whitespace-pre-wrap text-sm leading-6 text-slate-800">{result.content}</p>
      <dl className="mt-4 flex flex-wrap gap-x-5 gap-y-1 text-xs text-slate-500">
        <div>
          <dt className="inline font-semibold">Fusion: </dt>
          <dd className="inline">{result.fusion_score.toFixed(4)}</dd>
        </div>
        {result.similarity !== null && result.similarity !== undefined && (
          <div>
            <dt className="inline font-semibold">Semantic: </dt>
            <dd className="inline">{result.similarity.toFixed(4)}</dd>
          </div>
        )}
        {result.lexical_score !== null && result.lexical_score !== undefined && (
          <div>
            <dt className="inline font-semibold">Lexical: </dt>
            <dd className="inline">{result.lexical_score.toFixed(4)}</dd>
          </div>
        )}
      </dl>
    </article>
  );
}
