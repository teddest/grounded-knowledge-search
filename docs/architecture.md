# Architecture

Grounded Knowledge Search is a local educational document-search application. It deliberately keeps the major search stages visible instead of hiding them behind one opaque chatbot call.

## System overview

```text
Markdown/text corpus
        |
        v
Document discovery and section extraction
        |
        v
PostgreSQL document and section records
        |
        +-----------------------------+
        |                             |
        v                             v
OpenRouter embeddings          PostgreSQL lexical index
        |                             |
        +-------------+---------------+
                      v
             Hybrid retrieval + RRF
                      |
          +-----------+------------+
          |                        |
          v                        v
       Search                 Grounded answer
                                  |
                                  v
                         Sources and citations
```

## Monorepo layout

```text
apps/api/       FastAPI service and Python domain logic
apps/web/       Next.js App Router interface
packages/contracts/  OpenAPI-generated TypeScript types
documents/      Synthetic Northstar Relay corpus
evaluation-queries.json  Labeled retrieval questions
db/init/        PostgreSQL and pgvector initialization SQL
scripts/        Development, contract, and quality commands
openspec/       Proposal, design, specifications, and task plan
```

## API service

The FastAPI service owns:

- Document-set registration
- File discovery and parsing
- Section persistence
- Embedding generation and persistence
- Lexical and vector retrieval
- Reciprocal-rank fusion
- Grounded answer generation
- Retrieval evaluation

The service keeps external boundaries explicit:

- PostgreSQL is accessed through a document-store adapter.
- OpenRouter embeddings are accessed through an embedding-provider adapter.
- OpenRouter chat completion is accessed through a chat-provider adapter.
- Unit tests replace these boundaries with deterministic fakes.

## Web service

The Next.js application owns:

- Document-set selection
- Indexing controls and status
- Search forms and filters
- Ranked evidence display
- Grounded-answer display
- Source-reference dialogs
- About and educational navigation

Retrieval and ranking do not happen in the browser. The web application calls typed API-client functions generated from the FastAPI OpenAPI schema.

## Persistence model

The database contains:

- `document_sets` — registered roots and indexing status
- `documents` — metadata, source paths, versions, statuses, and content hashes
- `sections` — searchable content, headings, source locations, lexical vectors, and embeddings
- `index_runs` — ingestion progress and failure details

Embedding metadata records the model and input hash so unchanged sections can be skipped during repeated indexing.

## Local runtime

`./scripts/dev.sh` starts:

- PostgreSQL with pgvector
- FastAPI with reload enabled
- Next.js with reload-friendly bind mounts

The development script synchronizes pnpm and uv dependencies from their lockfiles before starting the services. The application uses standard local ports:

- Web: `3000`
- API: `8000`
- PostgreSQL: `5432`
