## 1. Runtime foundation — `chore/runtime-foundation` (PR 1)

- [ ] 1.1 Add the Python application package, dependency manifest, and development commands.
- [ ] 1.2 Add environment configuration for the database, document directory, OpenRouter key, embedding model, chat model, and embedding dimensions.
- [ ] 1.3 Add Docker Compose services for the application and PostgreSQL with the pgvector extension.
- [ ] 1.4 Add the initial database schema for repositories/documents, sections, metadata, and indexing state.
- [ ] 1.5 Add the FastAPI application shell and a database-backed health endpoint.
- [ ] 1.6 Add a safe `.env.example` and verify that no credentials are committed.
- [ ] 1.7 Document the commands for starting the empty application and checking its health.

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

## 7. Learning interface — `feat/search-interface` (PR 7)

- [ ] 7.1 Add a small browser interface for selecting a corpus, starting ingestion, and viewing indexing status.
- [ ] 7.2 Add a search view showing ranked sections, metadata, source paths, and retrieval diagnostics.
- [ ] 7.3 Add an answer view showing the generated response and its cited source sections.
- [ ] 7.4 Add clear configuration and provider-error messages for users without an OpenRouter key.
- [ ] 7.5 Verify the interface against the primary corpus questions without adding application-specific dataset naming.

## 8. Educational documentation — `docs/educational-guide` (PR 8)

- [ ] 8.1 Document the application architecture and the flow from documents to sections, embeddings, retrieval, and answers.
- [ ] 8.2 Document supported input formats, metadata conventions, chunking behavior, and known limitations.
- [ ] 8.3 Document the difference between lexical search, semantic search, hybrid ranking, and answer generation.
- [ ] 8.4 Document local setup, OpenRouter configuration, model compatibility, and external data-handling considerations.
- [ ] 8.5 Document how to add evaluation questions and interpret Hit@K, Precision@K, Recall@K, and MRR.
- [ ] 8.6 Add a troubleshooting guide for database startup, missing credentials, embedding dimensions, and empty results.
- [ ] 8.7 Run the documented clean-clone walkthrough and fix any setup gaps.
