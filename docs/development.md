# Development guide

## Repository rules

Read `AGENTS.md` before changing the repository. Work from a topic branch, never directly from `main`, and keep each branch focused on one OpenSpec task group.

The implementation plan is in:

```text
openspec/changes/document-search-foundation/
```

## Toolchain

- Node.js LTS pinned by the repository workflow
- pnpm workspace for the Next.js application and shared packages
- Python dependencies managed by uv
- FastAPI for the API
- Next.js App Router and TypeScript for the web application
- Tailwind CSS and shadcn/ui for styling and primitives
- PostgreSQL with pgvector for persistence and vector retrieval
- OpenRouter for configurable embeddings and chat completion

## Language boundaries

### Python

The API uses domain models, dependency injection, and ports/adapters at database and model-provider boundaries. Public functions are typed, errors are explicit, and core parsing/ranking/evaluation logic is deterministic.

Run:

```bash
cd apps/api
uv run pytest --cov=grounded_knowledge_api --cov-branch
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

### TypeScript and Next.js

The web app uses strict TypeScript, App Router server components by default, focused client components for interaction, typed API calls, accessible controls, and shadcn/ui source components owned by the repository.

Run:

```bash
pnpm --filter @grounded/web test:coverage
pnpm --filter @grounded/web typecheck
pnpm --filter @grounded/web lint
pnpm --filter @grounded/web build
pnpm --filter @grounded/web e2e
```

### SQL, shell, and Docker

SQL is parameterized and schema changes are versioned. Shell scripts use strict mode and are safe to rerun. Docker development services use health checks, lockfile-based installs, and bind mounts for reload.

## Contracts

FastAPI is the source of truth for the API schema. Regenerate TypeScript types with:

```bash
./scripts/generate-contracts.sh
```

Verify that generation does not create a diff:

```bash
./scripts/check-contracts.sh
```

## Supply-chain controls

- Commit `pnpm-lock.yaml` and `uv.lock`.
- Use frozen/locked installs.
- Keep registries explicit.
- Review lifecycle/build scripts.
- Avoid unpinned Git, URL, and local-path dependencies.
- Run Node and Python dependency audits.
- Never commit API keys or registry credentials.

## Complete verification

Use the single quality command before opening a PR:

```bash
./scripts/check.sh
```

The command runs tests, coverage, linting, type checks, builds, contract verification, browser tests, and dependency audits.
