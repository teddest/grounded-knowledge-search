## ADDED Requirements

### Requirement: The ingestion workflow SHALL support Markdown and plain-text documents
The system SHALL discover supported Markdown and plain-text files from a configured document directory and SHALL ignore unsupported files and common generated/dependency directories.

#### Scenario: Ingest the checked-in corpus
- **WHEN** ingestion runs against the repository document directory
- **THEN** it discovers the corpus documents and does not require a separate conversion step

#### Scenario: Encounter an unsupported file
- **WHEN** the document directory contains an unsupported file type
- **THEN** the ingestion workflow skips it and reports or records the skip without failing the entire run

### Requirement: Ingestion SHALL preserve section context
The system SHALL split documents into bounded searchable sections while preserving the document title, heading path, source path, and line range or equivalent location information.

#### Scenario: A document contains multiple headings
- **WHEN** the document is ingested
- **THEN** each resulting section identifies its heading context and can be traced back to the source document

### Requirement: Ingestion SHALL persist document metadata with each section
The system SHALL persist document and section metadata including document ID, title, category, status, version, effective date when present, source path, and section text.

#### Scenario: A current and archived policy are indexed
- **WHEN** both policy versions are ingested
- **THEN** search results can distinguish them using status, version, and effective-date metadata

### Requirement: Ingestion SHALL be repeatable
Re-ingesting the same document directory SHALL replace or update the prior records for that source without creating unbounded duplicate sections.

#### Scenario: A corpus is indexed twice
- **WHEN** the user runs ingestion twice without changing the documents
- **THEN** the indexed section count remains stable and the results do not contain duplicate copies caused by the second run

### Requirement: Ingestion SHALL report failures clearly
The workflow SHALL expose whether ingestion is running, complete, or failed and SHALL include an actionable error for malformed metadata, unavailable storage, or unavailable embedding configuration.

#### Scenario: The embedding provider is not configured
- **WHEN** ingestion needs embeddings and no provider key is configured
- **THEN** ingestion fails with a configuration message identifying the missing setting rather than silently creating incomplete records
