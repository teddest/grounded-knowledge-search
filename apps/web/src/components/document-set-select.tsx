"use client";

import type { DocumentSet } from "@/lib/api";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

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
  return (
    <Select value={selectedId} onValueChange={onChange} disabled={disabled}>
      <SelectTrigger id={id} aria-label="Indexed documents" className="w-full">
        <SelectValue placeholder="Select a document set" />
      </SelectTrigger>
      <SelectContent>
        {documentSets.length === 0 ? (
          <SelectItem value="__empty" disabled>
            No document sets available.
          </SelectItem>
        ) : (
          documentSets.map((documentSet) => (
            <SelectItem key={documentSet.id} value={documentSet.id}>
              {documentSet.name} ({documentSet.status})
            </SelectItem>
          ))
        )}
      </SelectContent>
    </Select>
  );
}
