#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [[ ! -f .env ]]; then
  cp .env.example .env
  printf '%s\n' "Created .env from .env.example. Add OPENROUTER_API_KEY when model requests are needed."
fi

docker compose build
# Keep bind-mounted dependency volumes in sync with the committed lockfiles.
docker compose run --rm --no-deps web pnpm install --frozen-lockfile
docker compose run --rm --no-deps api uv sync --locked

exec docker compose up "$@"
