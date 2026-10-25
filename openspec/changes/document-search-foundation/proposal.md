## Why

People often need to answer questions from a collection of policies, procedures, FAQs, and product documents, but keyword search alone misses paraphrased questions while ungrounded language-model answers can be difficult to trust. This change establishes a small, reproducible document-search system that demonstrates how semantic retrieval, lexical retrieval, source metadata, and citations work together in an educational setting.

The repository should be understandable and runnable by someone starting with no prior search infrastructure. A generated document corpus and labeled questions provide a consistent way to explore retrieval behavior, inspect failure cases, and measure improvements rather than relying on an opaque chatbot demo.

## What Changes

- Add a reproducible educational document corpus covering policies, procedures, product guidance, support information, and versioned documents.
- Add a local document-search application that can ingest the corpus and expose searchable document sections with source metadata.
- Add semantic retrieval backed by configurable OpenRouter embeddings.
- Add lexical and exact-term retrieval so that precise terms, dates, names, and policy versions are not dependent on embedding similarity.
- Combine retrieval signals into a ranked result set with document metadata and source locations.
- Add grounded question answering through a configurable OpenRouter chat model.
- Require generated answers to identify supporting source sections and acknowledge insufficient or conflicting evidence.
- Add a labeled evaluation set and reporting for Hit@K, Precision@K, Recall@K, MRR, and source/citation correctness.
- Add local Docker-based setup and educational documentation explaining the ingestion, retrieval, answer-generation, and evaluation flow.

## Capabilities

### New Capabilities

- `document-corpus`: Provides a reproducible, metadata-rich set of educational documents and representative search questions.
- `document-ingestion`: Parses supported documents into searchable sections while preserving titles, headings, versions, dates, and source locations.
- `hybrid-retrieval`: Searches document sections using semantic similarity, lexical matching, exact terms, and metadata filters, then returns ranked evidence.
- `grounded-answers`: Generates answers from retrieved document evidence and presents source citations and uncertainty.
- `retrieval-evaluation`: Runs labeled queries and reports ranking, retrieval, and citation-quality measures.
- `local-development`: Provides a reproducible local setup and documentation for running the system with Docker and OpenRouter configuration.

### Modified Capabilities

- None.

## Impact

- Adds the initial application, API, persistence, and user-facing documentation for the repository.
- Adds PostgreSQL with the pgvector extension as the local retrieval store.
- Adds an OpenRouter integration for embedding and chat model requests; model names and credentials remain configurable.
- Adds Docker-based local infrastructure and environment configuration.
- Introduces APIs or commands for document ingestion, search, grounded questions, and evaluation.
- Requires clear handling of external model requests because document content may be sent to OpenRouter.
- No existing production interfaces or capabilities are modified.
