## 1. Runtime foundation — `chore/runtime-foundation` (PR 1)

- [x] 1.1 Verify current official setup guidance for the supported Python version, Node.js LTS, pnpm, uv, FastAPI, Next.js App Router, TypeScript, Tailwind CSS, pytest, Vitest, and Playwright; record selected versions in lockfiles rather than relying on unverified assumptions.
- [x] 1.2 Create the monorepo application layout with `apps/api`, `apps/web`, `packages/contracts`, and `scripts`, plus root workspace configuration.
- [x] 1.3 Add the Python API dependency manifest and uv locked resolver workflow, formatting/linting/type-checking configuration, and test commands.
- [x] 1.4 Add the Next.js App Router TypeScript project using `src/`, pnpm workspace configuration, ESLint, Tailwind CSS through the current official integration, and frontend test commands.
- [x] 1.5 Add environment configuration for the database, document directory, OpenRouter key, embedding model, chat model, embedding dimensions, and API base URL.
- [x] 1.6 Add Docker Compose development services for the API, Next.js web application, and PostgreSQL with the pgvector extension, using bind mounts and named dependency volumes for reload-friendly development.
- [x] 1.7 Add the initial database schema for repositories/documents, sections, metadata, and indexing state.
- [x] 1.8 Add the FastAPI application shell and a database-backed health endpoint.
- [x] 1.9 Add the initial Next.js layout, accessible loading/error boundaries, and a health/configuration status surface.
- [x] 1.10 Generate the initial TypeScript API contract from the FastAPI OpenAPI schema into `packages/contracts` using a pinned pnpm tool.
- [x] 1.11 Add Python coverage configuration with branch coverage and the agreed near-100% gate for first-party logic.
- [x] 1.12 Add TypeScript coverage configuration with statement, branch, function, and line thresholds plus documented minimal exclusions.
- [x] 1.13 Add a safe `.env.example`, `pnpm-lock.yaml`, `uv.lock`, pinned package-manager versions, and verification that no credentials are committed.
- [x] 1.14 Add explicit registry configuration and reviewed lifecycle/build-script policy for pnpm and uv.
- [x] 1.15 Add `scripts/dev.sh` as the single development entry point and verify it starts every service with one command.
- [x] 1.16 Document the commands for starting the services and running API, web, type, lint, build, coverage, lockfile, and dependency security checks, including the hot-reload workflow.

## 2. Document model and ingestion — `feat/document-ingestion` (PR 2)

- [x] 2.1 Define the document and section domain models used by both ingestion and retrieval.
- [x] 2.2 Implement YAML front-matter parsing for the checked-in corpus metadata.
- [x] 2.3 Implement Markdown heading-aware section extraction with source line ranges.
- [x] 2.4 Implement plain-text section extraction with bounded section sizes.
- [x] 2.5 Implement supported-file discovery and skipping for unsupported, generated, and dependency directories.
- [x] 2.6 Add idempotent persistence that replaces a source document's prior sections on re-ingestion.
- [x] 2.7 Add ingestion status and error reporting for malformed metadata and unsupported inputs.
- [x] 2.8 Add unit tests for metadata parsing, section boundaries, skipped files, and repeated ingestion.

## 3. OpenRouter embeddings and indexing — `feat/embedding-indexing` (PR 3)

- [x] 3.1 Define an internal embedding-provider interface independent of the OpenRouter client.
- [x] 3.2 Implement the OpenRouter embeddings adapter using configurable model and request settings.
- [x] 3.3 Add batched embedding requests with bounded retries and actionable provider errors.
- [x] 3.4 Validate embedding dimensions before writing vectors to the database.
- [x] 3.5 Implement indexing orchestration from parsed sections through embeddings to persisted vector records.
- [x] 3.6 Ensure API keys, document content, and full embedding payloads are excluded from application logs.
- [x] 3.7 Add provider-mocked tests for successful batches, missing credentials, dimension mismatch, and retry failure.
- [x] 3.8 Add a corpus ingestion command or endpoint and verify that the checked-in dataset becomes searchable data.

## 4. Hybrid retrieval — `feat/hybrid-retrieval` (PR 4)

- [x] 4.1 Add PostgreSQL lexical indexes or query support for section text, titles, headings, and distinctive terms.
- [x] 4.2 Implement vector candidate retrieval with configurable top-k behavior.
- [x] 4.3 Implement lexical and exact-term candidate retrieval with repository/category/status/version filters.
- [x] 4.4 Implement reciprocal-rank fusion with duplicate section removal and component-rank diagnostics.
- [x] 4.5 Define the search response containing ranked text, source metadata, location, and retrieval diagnostics.
- [x] 4.6 Add the search API endpoint with validation for query, repository, filters, and result limit.
- [x] 4.7 Add tests for paraphrased queries, exact version terms, metadata filters, no-result queries, and stable ranking output.
- [x] 4.8 Compare vector-only, lexical-only, and hybrid behavior against a small set of manually inspected queries.

## 5. Grounded answers — `feat/grounded-answers` (PR 5)

- [x] 5.1 Define the bounded context format that labels each retrieved section with a stable citation number.
- [x] 5.2 Define the answer-generation prompt requiring evidence-only answers, citations, and explicit uncertainty.
- [x] 5.3 Implement the configurable OpenRouter chat adapter behind an internal interface.
- [x] 5.4 Implement the answer endpoint by reusing hybrid search and returning both the answer and source records.
- [x] 5.5 Add handling for no evidence, missing chat credentials, provider failure, and oversized context.
- [x] 5.6 Add tests using a mocked chat provider for citation formatting, insufficient evidence, and current-versus-archived metadata.
- [x] 5.7 Manually verify answers for the refund, failed-payment, export, and data-retention questions.

## 6. Retrieval evaluation — `feat/retrieval-evaluation` (PR 6)

- [x] 6.1 Define the evaluation input schema for queries, use cases, expected sources, and optional expected answer summaries.
- [x] 6.2 Implement source matching that distinguishes expected current and historical documents.
- [x] 6.3 Implement Hit@K, Precision@K, Recall@K, and reciprocal-rank calculations.
- [x] 6.4 Produce aggregate and per-query output containing expected sources, returned sources, and failure details.
- [x] 6.5 Add a command or endpoint that evaluates the checked-in question set through the normal retrieval path.
- [x] 6.6 Add unit tests for metric calculations, no-hit cases, multi-source recall, and version mismatch.
- [x] 6.7 Document citation correctness and answer groundedness as separate human-review dimensions.
- [x] 6.8 Run and record a baseline evaluation without presenting unmeasured performance claims.

## 7. Next.js learning interface — `feat/search-interface` (PR 7)

- [x] 7.1 Define typed API-client models and request functions for repositories, ingestion status, search, and grounded answers.
- [x] 7.2 Build the accessible document-set and indexing-status view with loading, empty, error, and retry states.
- [x] 7.3 Build the Tailwind-styled search form with query input and category/status/version filters.
- [x] 7.4 Build reusable result-card and source-detail components showing ranked evidence, metadata, excerpts, and locations.
- [x] 7.5 Build the grounded-answer view with citation markers linked to the returned source records.
- [x] 7.6 Keep interactive behavior in focused client components and keep non-interactive rendering in server components where appropriate.
- [x] 7.7 Add component and interaction tests for success, loading, empty, error, and citation states.
- [x] 7.8 Add the Playwright smoke flow for loading the app, searching, and inspecting a source using a deterministic backend fixture.
- [x] 7.9 Verify the interface against the primary corpus questions without adding application-specific dataset naming.

## 8. Quality gates and contract verification — `test/quality-gates` (PR 8)

- [ ] 8.1 Add deterministic fakes and dependency overrides for database, embedding, chat, and API-client boundaries.
- [ ] 8.2 Add Python unit, API, integration, and error-path tests for every implemented application module.
- [ ] 8.3 Add TypeScript unit and component tests for shared utilities and all first-party interactive components.
- [ ] 8.4 Add API contract tests for ingestion status, search results, and grounded-answer responses.
- [ ] 8.5 Add branch coverage reports and enforce 100% coverage for deterministic first-party Python and TypeScript logic, documenting any narrowly scoped exclusions.
- [ ] 8.6 Run linting, formatting, type checking, builds, unit tests, integration tests, and browser tests in one repeatable verification command.
- [ ] 8.7 Confirm that tests run without OpenRouter network access and that external calls are limited to explicitly marked integration checks.
- [ ] 8.8 Add frozen-install checks for pnpm and the Python dependency workflow.
- [ ] 8.9 Add package-manager audit and vulnerability checks for Node and Python dependencies.
- [ ] 8.10 Add lockfile, registry, lifecycle-script, dependency-source, and secret-leak checks with documented exceptions.
- [ ] 8.11 Verify the security workflow fails on a controlled vulnerable dependency fixture or equivalent deterministic test.

## 9. Educational documentation — `docs/educational-guide` (PR 9)

- [ ] 9.1 Document the application architecture and the flow from documents to sections, embeddings, retrieval, and answers.
- [ ] 9.2 Document the API/web split, Next.js App Router structure, TypeScript conventions, Tailwind setup, and component boundaries.
- [ ] 9.3 Document supported input formats, metadata conventions, chunking behavior, and known limitations.
- [ ] 9.4 Document the difference between lexical search, semantic search, hybrid ranking, and answer generation.
- [ ] 9.5 Document local setup, OpenRouter configuration, model compatibility, and external data-handling considerations.
- [ ] 9.6 Document testing layers, coverage commands, thresholds, and the difference between coverage and behavior quality.
- [ ] 9.7 Document how to add evaluation questions and interpret Hit@K, Precision@K, Recall@K, and MRR.
- [ ] 9.8 Add a troubleshooting guide for database startup, missing credentials, embedding dimensions, frontend/API connectivity, and empty results.
- [ ] 9.9 Run the documented clean-clone walkthrough and fix any setup gaps.
