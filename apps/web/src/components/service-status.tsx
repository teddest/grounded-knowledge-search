"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { fetchHealth } from "@/lib/api";

type Status =
  | { state: "checking" }
  | { state: "ready" }
  | { state: "unavailable"; message: string };

export function ServiceStatus(): React.JSX.Element {
  const [status, setStatus] = useState<Status>({ state: "checking" });

  useEffect(() => {
    let active = true;

    fetchHealth()
      .then(() => {
        if (active) setStatus({ state: "ready" });
      })
      .catch((error: unknown) => {
        if (!active) return;
        const message = error instanceof Error ? error.message : "The API is unavailable.";
        setStatus({ state: "unavailable", message });
      });

    return () => {
      active = false;
    };
  }, []);

  if (status.state === "checking") {
    return <Badge variant="secondary" role="status">Checking API and database status…</Badge>;
  }

  if (status.state === "unavailable") {
    return <Badge variant="destructive" role="alert">{status.message}</Badge>;
  }

  return <Badge variant="outline" role="status" className="text-emerald-700">API and database are ready.</Badge>;
}
