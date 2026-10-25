## Context

The repository currently contains a fictional document corpus, labeled evaluation questions, and an OpenSpec proposal, but no application runtime. The system will turn those materials into a locally runnable educational document-search application. It must be simple enough to inspect and extend while still demonstrating the major retrieval concerns: document structure, metadata, semantic similarity, exact terms, ranking, source authority, grounded answers, and evaluation.

The initial corpus consists of Markdown documents with YAML front matter and headings. The first implementation will support Markdown and plain text, use PostgreSQL with pgvector for persistence, and use OpenRouter through its OpenAI-compatible API for embeddings and chat completion. Docker Compose will provide the local runtime.

## Goals / Non-Goals

**Goals:**

- Provide a reproducible local path from documents to searchable sections.
- Preserve document metadata, headings, versions, effective dates, and source locations.
- Combine semantic retrieval with lexical and exact-term retrieval.
- Return inspectable ranked evidence before generating an answer.
- Generate answers that cite retrieved document sections and acknowledge insufficient evidence.
- Make the evaluation questions runnable against the same retrieval path used by the application.
- Keep external model configuration explicit and replaceable.
- Organize implementation into small, independently reviewable PRs.
- Use strong typing, explicit dependency boundaries, and automated quality gates in both application layers.
- Target 100% coverage for first-party deterministic application logic where practical, with end-to-end tests covering the primary user workflow.
- Keep the code in a monorepo with one documented development command and hot reload for local UI work.

**Non-Goals:**

- PDF, OCR, web crawling, or arbitrary document conversion in the first release.
- A graph database, graph traversal system, or autonomous action-taking agent.
- Production authentication, multi-tenancy, access control, or high-availability deployment.
- Guaranteed factual correctness from the language model without source inspection.
- Automatic policy approval, document mutation, or customer-facing workflow actions.
- Large-scale performance or cost claims.

## Decisions

### 1. Use a typed Python API and a separate Next.js web application

Use FastAPI for the HTTP API and a separate Next.js application written in TypeScript for the browser interface. Keep both applications in one monorepo with an explicit layout such as `apps/api`, `apps/web`, `packages/contracts`, and `scripts`. The Python service owns ingestion, retrieval, answer generation, and evaluation; the Next.js service owns routing, presentation, browser interactions, and a typed API client; the contracts package contains generated or centrally maintained API types.

The frontend will use the App Router, `src/` organization, server components by default, and client components only where interactivity requires them. The development container will bind-mount the web source and run the Next.js development server so edits trigger hot reload without rebuilding the image. The API will use its equivalent reload mode for backend changes.

The implementation will verify current stable framework guidance and commit lockfiles rather than assuming package versions. The frontend will use Tailwind CSS through the current official Next.js integration, with shared design tokens and reusable components instead of scattered ad hoc styles.

**Alternatives considered:** Serving static HTML from FastAPI would reduce setup but would not provide the requested Next.js/Tailwind learning surface. A single full-stack Next.js implementation would duplicate or replace the Python search service and make the retrieval architecture less explicit. A separate frontend repository would make local setup and coordinated changes harder.

### 2. Use PostgreSQL with pgvector as the retrieval store

Store documents, sections, metadata, embeddings, and indexing state in PostgreSQL. Use pgvector for vector similarity and PostgreSQL full-text search plus ordinary indexes for lexical and exact metadata retrieval. This keeps source metadata and retrieval records in one inspectable system and avoids adding a separate search service for the first release.

**Alternatives considered:** OpenSearch would provide more search-native features but adds another service and obscures the comparison between retrieval methods. A file-only index would not demonstrate persistence or vector search.

### 3. Preserve sections as the primary retrieval unit

Split Markdown by headings and plain text by paragraph/size boundaries. Each section stores the document ID, heading path, source path, line range when available, version, effective date, status, category, and text. Embeddings include the section title and relevant metadata so that short sections retain context.

**Alternatives considered:** Fixed-size chunks alone are easy but can separate a rule from its heading and make citations difficult. Full-document embeddings are too coarse for multi-topic documents.

### 4. Use hybrid retrieval with reciprocal-rank fusion

Run semantic and lexical searches independently, optionally apply metadata filters, deduplicate by section ID, and combine the ranked lists using reciprocal-rank fusion. Return component ranks and scores for inspection. Add exact matches for document IDs, titles, headings, and distinctive terms where practical.

**Alternatives considered:** Vector-only retrieval is weak for dates, versions, names, and exact policy language. A hand-tuned weighted score is harder to explain and calibrate before labels exist. A learned reranker is deferred until a labeled baseline exists.

### 5. Keep the model boundary behind an OpenAI-compatible adapter

Use configurable OpenRouter embedding and chat model names, API key, site URL, request timeout, and retry behavior. The rest of the application depends on an internal embedding/chat interface rather than the OpenRouter client directly. Model output is treated as untrusted text and is never allowed to issue application actions.

**Alternatives considered:** Direct provider-specific calls would make the educational example harder to replace. A local model would reduce external data transfer but would add hardware and model setup to the quick-start path.

### 6. Separate retrieval evidence from generated answers

The search endpoint returns ranked sections without requiring a chat model. The answer endpoint reuses search, formats a bounded evidence context, and asks the chat model to cite sources by stable result number. The API returns both the answer and the exact source records used to construct the context.

**Alternatives considered:** A single opaque question-answer endpoint would make relevance failures difficult to inspect and evaluate.

### 7. Treat evaluation as a first-class workflow

Keep the labeled questions in version control. The evaluator will call the same retrieval service, match returned source paths against expected sources, and report Hit@K, Precision@K, Recall@K, and MRR. Citation correctness and answer quality remain separately reviewable because automatic path matching cannot prove that a generated explanation is semantically correct.

**Alternatives considered:** Manual demos alone are not repeatable. LLM-as-judge evaluation is deferred because it introduces another model-dependent signal before the retrieval baseline is understood.

### 8. Use framework-appropriate testing and dependency seams

The Python service will use pytest, HTTPX/FastAPI test clients, fixtures, and dependency injection for database and model-provider boundaries. The Next.js service will use TypeScript, ESLint, Vitest, React Testing Library, and Playwright for browser workflows. External OpenRouter calls and database integrations will be tested through deterministic fakes or mocks, while a small number of integration tests verify real container wiring.

Every first-party module should be designed so its behavior can be tested without network access. Coverage will be measured separately for Python and TypeScript, include branch coverage, and fail CI when the agreed threshold is not met. The target is 100% for deterministic first-party logic and as close to 100% as practical for the complete application; generated files, framework scaffolding, and configuration-only files may be excluded only when the exclusion is documented.

**Alternatives considered:** Testing only through the browser would be slow and would leave domain logic under-tested. Unmocked model calls would be nondeterministic and expensive. A nominal coverage percentage without branch coverage would make the quality signal misleading.

### 9. Keep the web/API contract explicit

Define request and response schemas at the FastAPI boundary and maintain matching TypeScript types in the web application. Prefer a generated or centrally maintained contract when practical, and add contract tests for search, ingestion status, and grounded-answer responses. The frontend must not duplicate ranking or answer-generation logic.

**Alternatives considered:** Untyped ad hoc fetch calls are quick initially but make API drift and error handling difficult to detect. Moving retrieval logic into Next.js would create two sources of truth.

### 10. Use one development entry point with development-only mounts

Provide a single executable script, `scripts/dev.sh`, that starts the database, API, and Next.js web service through Docker Compose. The development Compose configuration will bind-mount source directories, retain dependency directories in named volumes, expose the web port, and enable file watching/reload. Development mounts and production-like images remain separate concerns even if the first release only documents local development.

**Alternatives considered:** Asking users to start three terminals is error-prone. Rebuilding the web image after every edit defeats hot reload. Running the database directly on the host makes the setup less reproducible.

## Risks / Trade-offs

- **[External model availability]** → Embedding and chat models may differ by OpenRouter account or change over time. Keep both model names configurable, fail with actionable errors, and document the required embedding dimension.
- **[Sensitive content transfer]** → Documents sent to OpenRouter leave the local environment. Use synthetic data by default, display the data-handling warning, and never log document content or API keys.
- **[Poor chunk boundaries]** → Heading-based sections may be too large or too small. Preserve source metadata, expose section text in search results, and add chunking examples to the documentation.
- **[Version conflicts]** → A search result may surface an archived policy next to a current policy. Store status and effective date, expose them in results, and add current-version filtering and evaluation cases.
- **[Ranking quality]** → RRF is a transparent baseline, not a guarantee of good relevance. Keep component scores visible and use the labeled evaluation set to guide future ranking changes.
- **[Synchronous indexing]** → Initial indexing may be slow for larger corpora. Keep the first workflow synchronous and bounded; defer background jobs until the behavior is correct.
- **[Citation illusion]** → A cited section may not fully support a generated claim. Return source text alongside every answer and document citation review as a separate evaluation step.
- **[Frontend/backend drift]** → Independently evolving Python and TypeScript types can disagree. Keep API schemas explicit, add contract tests, and regenerate or review client types as part of API changes.
- **[Coverage-driven test brittleness]** → A 100% target can encourage tests that assert implementation details. Prefer behavior-level tests, use dependency seams, and document justified exclusions rather than lowering the target silently.
- **[Framework churn]** → Next.js and Tailwind integration details change over time. Verify official setup documentation at implementation time and commit lockfiles and tested configuration.
- **[Container file watching]** → Bind-mounted file events can behave differently across operating systems. Use the documented polling fallback only when needed, keep the reload command observable, and verify edits inside the web container.
- **[Monorepo coupling]** → Shared contracts can create unnecessary coordination between API and web changes. Keep the contracts package narrow, generate or validate it from the API schema, and version behavior changes through OpenSpec.

## Migration Plan

There is no existing application data or production deployment to migrate. Implementation proceeds from the checked-in corpus:

1. Copy the example environment configuration and run `./scripts/dev.sh` to start PostgreSQL/pgvector, the Python API, and the Next.js web application.
2. Verify that editing a web source file updates the browser without rebuilding the image and that API edits trigger backend reload.
3. Configure an OpenRouter key and compatible embedding/chat models.
4. Run the automated Python and TypeScript checks before starting interactive use.
5. Run the corpus ingestion command or endpoint.
6. Verify search results before enabling answer generation.
7. Run the labeled evaluation suite and record baseline metrics.
8. Add later retrieval improvements by comparing them against the baseline.

Rollback is removing or recreating the local Docker volume and returning to the previous Git branch. No external service state is modified by the application.

## Open Questions

- Which OpenRouter embedding model should be the documented default? Select one available model after verifying its endpoint and vector dimension during implementation.
- Should API client types be generated from the FastAPI OpenAPI schema or maintained in a small checked-in TypeScript contract module? Decide during the runtime-foundation branch and cover the choice with contract tests.
- Which browser-level flow should be the required Playwright smoke test? The minimum candidate is ingest status → search → inspect source → ask a cited question.
- Should file watching use native events by default with an opt-in polling flag, or use polling in all development containers for consistency? Verify on the supported development environments during implementation.
