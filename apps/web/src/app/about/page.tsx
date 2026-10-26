import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

const sections = [
  {
    title: "What this application does",
    body: "Grounded Knowledge Search helps people find evidence in policies, procedures, FAQs, and product documents. It combines semantic retrieval with lexical matching, then can generate an answer tied to the retrieved sources.",
  },
  {
    title: "How the data flows",
    body: "Documents are parsed into metadata-rich sections. Sections are stored in PostgreSQL, embedded through OpenRouter, and indexed with pgvector plus PostgreSQL full-text search. Search results are fused and passed as bounded evidence to the answer model.",
  },
  {
    title: "Retrieval and ranking",
    body: "Vector search handles paraphrased questions. Lexical and exact-term search handles identifiers, dates, versions, and policy language. Reciprocal-rank fusion combines the candidate lists while preserving component diagnostics for inspection.",
  },
  {
    title: "Grounded answers",
    body: "The answer workflow receives only retrieved sections, includes document status and version context, and asks the model to cite source numbers. When evidence is missing, the application is expected to say so rather than inventing a rule.",
  },
  {
    title: "Evaluation",
    body: "The repository includes labeled questions and an evaluation endpoint for Hit@K, Precision@K, Recall@K, and MRR. Retrieval metrics are kept separate from citation correctness and generated-answer quality, which require additional review.",
  },
  {
    title: "Technology and boundaries",
    body: "The application is a pnpm/uv monorepo with a Next.js and TypeScript interface, shadcn/ui and Tailwind CSS, a FastAPI service, PostgreSQL with pgvector, and configurable OpenRouter models. It is an educational system, not a graph database or an autonomous action-taking agent.",
  },
];

export default function AboutPage(): React.JSX.Element {
  return (
    <main className="mx-auto min-h-screen max-w-6xl px-6 py-10">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-sky-700">
            Grounded Knowledge Search
          </p>
          <h1 className="mt-3 text-4xl font-bold tracking-tight text-slate-950">About the application</h1>
          <p className="mt-3 max-w-3xl text-lg text-slate-600">
            A transparent learning project for exploring document ingestion, hybrid retrieval,
            grounded generation, and search evaluation.
          </p>
        </div>
        <Button size="lg" className="shadow-sm" asChild>
          <Link href="/">
            <ArrowLeft />
            Back to search
          </Link>
        </Button>
      </header>

      <div className="mt-8 grid gap-5 md:grid-cols-2">
        {sections.map((section) => (
          <Card key={section.title} className="border-slate-200 shadow-sm">
            <CardHeader>
              <h2 className="font-heading text-base leading-snug font-medium">{section.title}</h2>
            </CardHeader>
            <CardContent>
              <p className="leading-7 text-slate-700">{section.body}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="mt-5 border-amber-200 bg-amber-50 shadow-sm">
        <CardHeader>
          <h2 className="font-heading text-base leading-snug font-medium">Data handling and limitations</h2>
        </CardHeader>
        <CardContent className="space-y-3 text-sm leading-6 text-amber-950">
          <p>
            The example corpus is synthetic. When you use your own documents, embedding and chat
            requests may send document content to the configured OpenRouter provider.
          </p>
          <p>
            Always inspect cited evidence. Search relevance, model correctness, and citation
            quality are related but different properties.
          </p>
        </CardContent>
      </Card>
    </main>
  );
}
