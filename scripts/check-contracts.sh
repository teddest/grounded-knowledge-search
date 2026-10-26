#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

./scripts/generate-contracts.sh

git diff --exit-code -- packages/contracts/openapi.json packages/contracts/src/generated.ts
