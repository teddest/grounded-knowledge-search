import { ServiceStatus } from "@/components/service-status";

export default function HomePage(): React.JSX.Element {
  return (
    <main className="mx-auto min-h-screen max-w-5xl px-6 py-12">
      <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wide text-sky-700">
          Grounded Knowledge Search
        </p>
        <h1 className="mt-3 text-4xl font-bold tracking-tight text-slate-950">
          Search documents with evidence.
        </h1>
        <p className="mt-4 max-w-2xl text-lg text-slate-600">
          The runtime foundation is ready. Document ingestion, hybrid retrieval, and cited answers
          will build on this API and web boundary.
        </p>
        <div className="mt-8 rounded-xl bg-slate-50 p-4">
          <ServiceStatus />
        </div>
      </div>
    </main>
  );
}
