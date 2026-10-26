#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

printf '%s\n' "==> Installing locked Node dependencies"
pnpm install --frozen-lockfile

printf '%s\n' "==> Installing locked Python dependencies"
uv sync --project apps/api --all-groups --locked

printf '%s\n' "==> Checking generated API contracts"
./scripts/check-contracts.sh

printf '%s\n' "==> Checking Python API"
(
  cd apps/api
  uv run pytest --cov=grounded_knowledge_api --cov-branch --cov-report=term-missing
  uv run ruff check .
  uv run ruff format --check .
  uv run mypy src
)

printf '%s\n' "==> Checking web application"
pnpm --filter @grounded/web test:coverage
pnpm --filter @grounded/web typecheck
pnpm --filter @grounded/web lint
pnpm --filter @grounded/web build
pnpm --filter @grounded/web e2e

printf '%s\n' "==> Checking Node dependencies"
pnpm audit --audit-level high

printf '%s\n' "==> Checking Python dependencies"
uv export --project apps/api --locked --all-groups --format requirements-txt --no-emit-project \
  > /tmp/grounded-knowledge-requirements.txt
uv run --project apps/api pip-audit --strict --require-hashes \
  -r /tmp/grounded-knowledge-requirements.txt

printf '%s\n' "All quality checks passed."
