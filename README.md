# Grounded Knowledge Search

This repository contains an educational document-search application and a fictional policy and procedure corpus.

## Run locally

Prerequisites:

- Docker Desktop or Docker Engine with Compose
- Node.js and pnpm versions defined by the repository configuration
- uv for Python dependency management

Start the database, API, and Next.js web application with one command:

```bash
./scripts/dev.sh
```

The script creates `.env` from `.env.example` when needed. The default local endpoints are:

- Web application: <http://localhost:3000>
- API health check: <http://localhost:8000/health>
- PostgreSQL: `localhost:5432`

The development containers bind-mount application source and use reload-friendly file watching. Add an `OPENROUTER_API_KEY` to `.env` when embedding or chat requests are implemented.

Run the current foundation checks with:

```bash
cd apps/api
uv run pytest --cov=grounded_knowledge_api --cov-branch
uv run ruff check .
uv run ruff format --check .
uv run mypy src

cd ../..
pnpm --filter @grounded/web test:coverage
pnpm --filter @grounded/web typecheck
pnpm --filter @grounded/web lint
pnpm --filter @grounded/web build
```

## Ingest a document set

Register a directory relative to the configured repository root:

```bash
curl -X POST http://localhost:8000/api/v1/document-sets \
  -H 'Content-Type: application/json' \
  -d '{"name":"policies","path":"policies"}'
```

Use the returned `id` to ingest the Markdown and text documents:

```bash
curl -X POST \
  http://localhost:8000/api/v1/document-sets/DOCUMENT_SET_ID/ingest
```

Generate and persist OpenRouter embeddings for the ingested sections:

```bash
curl -X POST \
  http://localhost:8000/api/v1/document-sets/DOCUMENT_SET_ID/index
```

The indexing endpoint batches embedding requests and skips sections already indexed with the configured embedding model. The ingestion workflow preserves front-matter metadata, headings, source paths, line ranges, content hashes, and searchable sections. Repeating ingestion replaces the existing records for that source instead of creating duplicates.

Search the indexed document set with hybrid vector and lexical retrieval:

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H 'Content-Type: application/json' \
  -d '{
    "document_set_id":"DOCUMENT_SET_ID",
    "query":"What is the annual refund window?",
    "limit":5,
    "filters":{"status":"current"}
  }'
```

Results include source metadata, excerpts, component ranks, similarity/lexical scores, and the reciprocal-rank fusion score.

## Dataset

**Northstar Relay** is the example dataset. It covers billing, onboarding, product behavior, support escalation, security, and incident response.

## Project planning

The implementation is planned with [OpenSpec](https://github.com/Fission-AI/OpenSpec). The proposal, design, requirements, and PR-sized task plan are in `openspec/changes/document-search-foundation/`.

## Document conventions

Each document begins with YAML front matter containing metadata that a search system can index:

- `title`
- `document_id`
- `category`
- `status`
- `version`
- `effective_date`
- `audience`
- `owner`

The 2024 and 2025 refund policies intentionally overlap. The 2025 policy is current and should take precedence when a question asks for the current policy. The 2024 policy remains useful for historical questions.

## Suggested search questions

- Can an annual customer receive a refund after 30 days?
- What happens after a payment fails?
- When should support escalate a failed payment?
- What changed in the refund policy between 2024 and 2025?
- How do I export a workspace?
- Which role can export customer data?
- What is the process for onboarding a new customer?
- How long are deleted workspace records retained?
- What should support do during a security incident?
- Is there a policy for exceptions to the standard refund window?

This corpus is synthetic and contains no real customer or company data.
