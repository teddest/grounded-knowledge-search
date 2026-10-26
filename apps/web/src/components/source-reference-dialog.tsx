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
            <div className="max-h-[60vh] overflow-auto rounded-lg border border-slate-200 bg-slate-950 text-sm text-slate-100">
              <pre className="min-w-full p-4">
                {lines.map((line, index) => (
                  <div className="flex" key={`${source.id}-${index}`}>
                    <span className="mr-4 inline-block w-10 shrink-0 select-none text-right text-slate-500">
                      {source.start_line == null ? "?" : source.start_line + index}
                    </span>
                    <span className="whitespace-pre-wrap break-words">{line || " "}</span>
                  </div>
                ))}
              </pre>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
