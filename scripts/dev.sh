#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [[ ! -f .env ]]; then
  cp .env.example .env
  printf '%s\n' "Created .env from .env.example. Add OPENROUTER_API_KEY when model requests are needed."
fi

exec docker compose up --build "$@"
