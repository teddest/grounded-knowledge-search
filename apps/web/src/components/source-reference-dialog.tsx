import { Streamdown } from "streamdown";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import type { SearchResult } from "@/lib/api";

type SourceReferenceDialogProps = {
  source: SearchResult | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export function SourceReferenceDialog({
  source,
  open,
  onOpenChange,
}: SourceReferenceDialogProps): React.JSX.Element {
  const lines = source?.content.split("\n") ?? [];
  const startLine = source?.start_line;
  const endLine = source?.end_line;
  const lineNumbers = startLine != null && endLine != null
    ? Array.from({ length: endLine - startLine + 1 }, (_, index) => startLine + index)
    : lines.map(() => "?");

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl">
        {source && (
          <>
            <DialogHeader>
              <DialogTitle>{source.title}</DialogTitle>
              <DialogDescription>
                {source.source_path}:{source.start_line ?? "?"}-{source.end_line ?? "?"}
              </DialogDescription>
            </DialogHeader>
            <div className="flex flex-wrap gap-2">
              <Badge variant="secondary">{source.status ?? "unknown status"}</Badge>
              <Badge variant="outline">{source.version ?? "unversioned"}</Badge>
              {source.heading_path?.map((heading) => (
                <Badge key={heading} variant="outline">
                  {heading}
                </Badge>
              ))}
            </div>
            <div className="mt-4 flex max-h-[60vh] overflow-auto rounded-lg border border-slate-200 bg-slate-950 text-sm text-slate-100">
              <div aria-hidden="true" className="shrink-0 border-r border-slate-800 px-3 py-4 text-right font-mono text-slate-500">
                {lineNumbers.map((lineNumber, index) => (
                  <div key={`${source.id}-line-${index}`} className="leading-6">
                    {lineNumber}
                  </div>
                ))}
              </div>
              <div className="min-w-0 p-4 [&_a]:text-sky-300 [&_code]:text-sky-200 [&_pre]:bg-slate-900 [&_strong]:text-white">
                <Streamdown mode="static" className="text-slate-100">
                  {source.content}
                </Streamdown>
              </div>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
