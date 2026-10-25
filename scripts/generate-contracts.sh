#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OPENAPI_FILE="$ROOT_DIR/packages/contracts/openapi.json"
GENERATED_FILE="$ROOT_DIR/packages/contracts/src/generated.ts"

OPENAPI_FILE="$OPENAPI_FILE" uv run --project "$ROOT_DIR/apps/api" python -c '
import json
import os
from pathlib import Path
from grounded_knowledge_api.main import app

Path(os.environ["OPENAPI_FILE"]).write_text(json.dumps(app.openapi(), indent=2) + "\n", encoding="utf-8")
'
pnpm exec openapi-typescript "$OPENAPI_FILE" -o "$GENERATED_FILE"
