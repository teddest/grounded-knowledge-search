"use client";

import { useEffect, useState } from "react";

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
    return <p role="status">Checking API and database status…</p>;
  }

  if (status.state === "unavailable") {
    return (
      <p role="alert" className="text-red-700">
        {status.message}
      </p>
    );
  }

  return (
    <p role="status" className="text-emerald-700">
      API and database are ready.
    </p>
  );
}
