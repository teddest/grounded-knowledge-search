import { Streamdown } from "streamdown";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import type { SearchResult } from "@/lib/api";

type ResultCardProps = {
  result: SearchResult;
  rank: number;
};

export function ResultCard({ result, rank }: ResultCardProps): React.JSX.Element {
  const location = `${result.source_path}:${result.start_line ?? "?"}-${result.end_line ?? "?"}`;
  const heading = result.heading_path?.join(" > ") || "Document";

  return (
    <Card className="border-slate-200 shadow-sm">
      <CardContent className="p-5">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <h3 className="font-semibold text-slate-950">
            <span className="mr-2 text-sky-700">#{rank}</span>
            {result.title}
          </h3>
          <code className="text-xs text-slate-500">{location}</code>
        </div>
        <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-slate-600">
          <span>{heading}</span>
          <Badge variant="secondary">{result.status ?? "unknown status"}</Badge>
          <Badge variant="outline">{result.version ?? "unversioned"}</Badge>
        </div>
        <Streamdown mode="static" className="mt-4 text-sm leading-6 text-slate-800">
          {result.content}
        </Streamdown>
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
      </CardContent>
    </Card>
  );
}
