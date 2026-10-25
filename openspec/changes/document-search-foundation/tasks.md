## 1. Runtime foundation — `chore/runtime-foundation` (PR 1)

- [ ] 1.1 Verify current official setup guidance for FastAPI, Next.js App Router, TypeScript, Tailwind CSS, pytest, Vitest, and Playwright; record selected versions in lockfiles rather than relying on unverified assumptions.
- [ ] 1.2 Create the monorepo application layout with `apps/api`, `apps/web`, `packages/contracts`, and `scripts`, plus root workspace configuration.
- [ ] 1.3 Add the Python API dependency manifest, formatting/linting/type-checking configuration, and test commands.
- [ ] 1.4 Add the Next.js App Router TypeScript project using `src/`, ESLint, Tailwind CSS through the current official integration, and frontend test commands.
- [ ] 1.5 Add environment configuration for the database, document directory, OpenRouter key, embedding model, chat model, embedding dimensions, and API base URL.
- [ ] 1.6 Add Docker Compose development services for the API, Next.js web application, and PostgreSQL with the pgvector extension, using bind mounts and named dependency volumes for reload-friendly development.
- [ ] 1.7 Add the initial database schema for repositories/documents, sections, metadata, and indexing state.
- [ ] 1.8 Add the FastAPI application shell and a database-backed health endpoint.
- [ ] 1.9 Add the initial Next.js layout, accessible loading/error boundaries, and a health/configuration status surface.
- [ ] 1.10 Add Python coverage configuration with branch coverage and the agreed near-100% gate for first-party logic.
- [ ] 1.11 Add TypeScript coverage configuration with statement, branch, function, and line thresholds plus documented minimal exclusions.
- [ ] 1.12 Add a safe `.env.example`, lockfiles, and verification that no credentials are committed.
- [ ] 1.13 Add `scripts/dev.sh` as the single development entry point and verify it starts every service with one command.
- [ ] 1.14 Document the commands for starting the services and running API, web, type, lint, build, and coverage checks, including the hot-reload workflow.

## 2. Document model and ingestion — `feat/document-ingestion` (PR 2)

- [ ] 2.1 Define the document and section domain models used by both ingestion and retrieval.
- [ ] 2.2 Implement YAML front-matter parsing for the checked-in corpus metadata.
- [ ] 2.3 Implement Markdown heading-aware section extraction with source line ranges.
- [ ] 2.4 Implement plain-text section extraction with bounded section sizes.
- [ ] 2.5 Implement supported-file discovery and skipping for unsupported, generated, and dependency directories.
- [ ] 2.6 Add idempotent persistence that replaces a source document's prior sections on re-ingestion.
- [ ] 2.7 Add ingestion status and error reporting for malformed metadata and unsupported inputs.
- [ ] 2.8 Add unit tests for metadata parsing, section boundaries, skipped files, and repeated ingestion.

## 3. OpenRouter embeddings and indexing — `feat/embedding-indexing` (PR 3)

- [ ] 3.1 Define an internal embedding-provider interface independent of the OpenRouter client.
- [ ] 3.2 Implement the OpenRouter embeddings adapter using configurable model and request settings.
- [ ] 3.3 Add batched embedding requests with bounded retries and actionable provider errors.
- [ ] 3.4 Validate embedding dimensions before writing vectors to the database.
- [ ] 3.5 Implement indexing orchestration from parsed sections through embeddings to persisted vector records.
- [ ] 3.6 Ensure API keys, document content, and full embedding payloads are excluded from application logs.
- [ ] 3.7 Add provider-mocked tests for successful batches, missing credentials, dimension mismatch, and retry failure.
- [ ] 3.8 Add a corpus ingestion command or endpoint and verify that the checked-in dataset becomes searchable data.

## 4. Hybrid retrieval — `feat/hybrid-retrieval` (PR 4)

- [ ] 4.1 Add PostgreSQL lexical indexes or query support for section text, titles, headings, and distinctive terms.
- [ ] 4.2 Implement vector candidate retrieval with configurable top-k behavior.
- [ ] 4.3 Implement lexical and exact-term candidate retrieval with repository/category/status/version filters.
- [ ] 4.4 Implement reciprocal-rank fusion with duplicate section removal and component-rank diagnostics.
- [ ] 4.5 Define the search response containing ranked text, source metadata, location, and retrieval diagnostics.
- [ ] 4.6 Add the search API endpoint with validation for query, repository, filters, and result limit.
- [ ] 4.7 Add tests for paraphrased queries, exact version terms, metadata filters, no-result queries, and stable ranking output.
- [ ] 4.8 Compare vector-only, lexical-only, and hybrid behavior against a small set of manually inspected queries.

## 5. Grounded answers — `feat/grounded-answers` (PR 5)

- [ ] 5.1 Define the bounded context format that labels each retrieved section with a stable citation number.
- [ ] 5.2 Define the answer-generation prompt requiring evidence-only answers, citations, and explicit uncertainty.
- [ ] 5.3 Implement the configurable OpenRouter chat adapter behind an internal interface.
- [ ] 5.4 Implement the answer endpoint by reusing hybrid search and returning both the answer and source records.
- [ ] 5.5 Add handling for no evidence, missing chat credentials, provider failure, and oversized context.
- [ ] 5.6 Add tests using a mocked chat provider for citation formatting, insufficient evidence, and current-versus-archived metadata.
- [ ] 5.7 Manually verify answers for the refund, failed-payment, export, and data-retention questions.

## 6. Retrieval evaluation — `feat/retrieval-evaluation` (PR 6)

- [ ] 6.1 Define the evaluation input schema for queries, use cases, expected sources, and optional expected answer summaries.
- [ ] 6.2 Implement source matching that distinguishes expected current and historical documents.
- [ ] 6.3 Implement Hit@K, Precision@K, Recall@K, and reciprocal-rank calculations.
- [ ] 6.4 Produce aggregate and per-query output containing expected sources, returned sources, and failure details.
- [ ] 6.5 Add a command or endpoint that evaluates the checked-in question set through the normal retrieval path.
- [ ] 6.6 Add unit tests for metric calculations, no-hit cases, multi-source recall, and version mismatch.
- [ ] 6.7 Document citation correctness and answer groundedness as separate human-review dimensions.
- [ ] 6.8 Run and record a baseline evaluation without presenting unmeasured performance claims.

## 7. Next.js learning interface — `feat/search-interface` (PR 7)

- [ ] 7.1 Define typed API-client models and request functions for repositories, ingestion status, search, and grounded answers.
- [ ] 7.2 Build the accessible document-set and indexing-status view with loading, empty, error, and retry states.
- [ ] 7.3 Build the Tailwind-styled search form with query input and category/status/version filters.
- [ ] 7.4 Build reusable result-card and source-detail components showing ranked evidence, metadata, excerpts, and locations.
- [ ] 7.5 Build the grounded-answer view with citation markers linked to the returned source records.
- [ ] 7.6 Keep interactive behavior in focused client components and keep non-interactive rendering in server components where appropriate.
- [ ] 7.7 Add component and interaction tests for success, loading, empty, error, and citation states.
- [ ] 7.8 Add the Playwright smoke flow for loading the app, searching, and inspecting a source using a deterministic backend fixture.
- [ ] 7.9 Verify the interface against the primary corpus questions without adding application-specific dataset naming.

## 8. Quality gates and contract verification — `test/quality-gates` (PR 8)

- [ ] 8.1 Add deterministic fakes and dependency overrides for database, embedding, chat, and API-client boundaries.
- [ ] 8.2 Add Python unit, API, integration, and error-path tests for every implemented application module.
- [ ] 8.3 Add TypeScript unit and component tests for shared utilities and all first-party interactive components.
- [ ] 8.4 Add API contract tests for ingestion status, search results, and grounded-answer responses.
- [ ] 8.5 Add branch coverage reports and enforce 100% coverage for deterministic first-party Python and TypeScript logic, documenting any narrowly scoped exclusions.
- [ ] 8.6 Run linting, formatting, type checking, builds, unit tests, integration tests, and browser tests in one repeatable verification command.
- [ ] 8.7 Confirm that tests run without OpenRouter network access and that external calls are limited to explicitly marked integration checks.

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
