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

**Non-Goals:**

- PDF, OCR, web crawling, or arbitrary document conversion in the first release.
- A graph database, graph traversal system, or autonomous action-taking agent.
- Production authentication, multi-tenancy, access control, or high-availability deployment.
- Guaranteed factual correctness from the language model without source inspection.
- Automatic policy approval, document mutation, or customer-facing workflow actions.
- Large-scale performance or cost claims.

## Decisions

### 1. Use a small Python HTTP application

Use FastAPI for a thin HTTP API and a small browser interface. Keep ingestion, retrieval, answer generation, and evaluation in separate modules so each part can be read independently. A CLI may call the same HTTP endpoints later, but the API is the first integration boundary.

**Alternatives considered:** A notebook would be quick but would not demonstrate a repeatable service boundary. A larger framework would add structure that is not needed for the educational scope.

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

## Risks / Trade-offs

- **[External model availability]** → Embedding and chat models may differ by OpenRouter account or change over time. Keep both model names configurable, fail with actionable errors, and document the required embedding dimension.
- **[Sensitive content transfer]** → Documents sent to OpenRouter leave the local environment. Use synthetic data by default, display the data-handling warning, and never log document content or API keys.
- **[Poor chunk boundaries]** → Heading-based sections may be too large or too small. Preserve source metadata, expose section text in search results, and add chunking examples to the documentation.
- **[Version conflicts]** → A search result may surface an archived policy next to a current policy. Store status and effective date, expose them in results, and add current-version filtering and evaluation cases.
- **[Ranking quality]** → RRF is a transparent baseline, not a guarantee of good relevance. Keep component scores visible and use the labeled evaluation set to guide future ranking changes.
- **[Synchronous indexing]** → Initial indexing may be slow for larger corpora. Keep the first workflow synchronous and bounded; defer background jobs until the behavior is correct.
- **[Citation illusion]** → A cited section may not fully support a generated claim. Return source text alongside every answer and document citation review as a separate evaluation step.

## Migration Plan

There is no existing application data or production deployment to migrate. Implementation proceeds from the checked-in corpus:

1. Start PostgreSQL/pgvector and the application with Docker Compose.
2. Configure an OpenRouter key and compatible embedding/chat models.
3. Run the corpus ingestion command or endpoint.
4. Verify search results before enabling answer generation.
5. Run the labeled evaluation suite and record baseline metrics.
6. Add later retrieval improvements by comparing them against the baseline.

Rollback is removing or recreating the local Docker volume and returning to the previous Git branch. No external service state is modified by the application.

## Open Questions

- Should the first browser interface be a static page served by FastAPI or a separate frontend? The initial design assumes a static page to keep local setup small.
- Should current-document filtering be automatic for current-policy queries or always explicit? The first release will expose metadata and support an explicit filter rather than infer user intent.
- Which OpenRouter embedding model should be the documented default? Select one available model after verifying its endpoint and vector dimension during implementation.
