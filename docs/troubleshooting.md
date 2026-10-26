# Troubleshooting

## Port already in use

The default ports are 3000, 8000, and 5432. Check for conflicts:

```bash
lsof -nP -iTCP:3000 -sTCP:LISTEN
lsof -nP -iTCP:8000 -sTCP:LISTEN
lsof -nP -iTCP:5432 -sTCP:LISTEN
```

Override ports in `.env` if needed:

```dotenv
WEB_PORT=3001
API_PORT=8001
POSTGRES_PORT=5433
NEXT_PUBLIC_API_BASE_URL=http://localhost:8001
```

## Database schema does not match the code

Docker initialization SQL runs when the PostgreSQL volume is created. For a disposable local database, reset it:

```bash
docker compose down -v
./scripts/dev.sh
```

Do not use `down -v` if the local database contains data you need to preserve.

## Missing OpenRouter key

Health checks, unit tests, and the deterministic Playwright test do not require an OpenRouter key. Embedding and grounded-answer requests do.

Check without printing the key:

```bash
grep -q '^OPENROUTER_API_KEY=.' .env \
  && echo configured \
  || echo missing
```

## No document sets appear

The web application creates an `All documents` set for the `documents/` directory when one does not already exist. Refresh the page after the API is available.

You can inspect sets directly:

```bash
curl http://localhost:8000/api/v1/document-sets
```

## Empty search results

Check that the selected set has been:

1. Ingested
2. Indexed for embeddings
3. Indexed with the expected filters

Useful checks:

```bash
curl http://localhost:8000/api/v1/document-sets

docker compose exec db psql -U search -d search \
  -c 'SELECT count(*) FROM sections;'

docker compose exec db psql -U search -d search \
  -c 'SELECT count(*) FROM sections WHERE embedding IS NOT NULL;'
```

## Embedding dimension errors

The PostgreSQL vector column and the configured embedding model must use the same dimension. The default is 1536 for `openai/text-embedding-3-small`.

Check:

```dotenv
OPENROUTER_EMBEDDING_MODEL=openai/text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
```

## UI does not hot reload

The development runtime uses bind mounts and polling. Check that the containers are running and inspect logs:

```bash
docker compose ps
docker compose logs -f web
docker compose logs -f api
```

If dependencies changed, rerun:

```bash
./scripts/dev.sh
```

## Contract generation creates a diff

Run:

```bash
./scripts/generate-contracts.sh
git diff -- packages/contracts/openapi.json packages/contracts/src/generated.ts
```

API changes should regenerate and commit the corresponding contract files.

## Playwright cannot connect

The Playwright configuration starts the Next.js development server automatically when needed. Run it from the web workspace:

```bash
pnpm --filter @grounded/web e2e
```

The smoke test stubs API responses and does not require PostgreSQL or OpenRouter.
