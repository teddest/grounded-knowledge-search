## ADDED Requirements

### Requirement: Search SHALL return ranked document evidence
The system SHALL accept a natural-language query and return ranked document sections containing source path, title, heading, metadata, location, text, and retrieval details.

#### Scenario: A user searches for a policy answer
- **WHEN** the user submits a query about refund eligibility
- **THEN** the response contains ranked sections from the relevant policy or support documents and enough source information to inspect them

### Requirement: Retrieval SHALL combine semantic and lexical signals
The system SHALL support semantic vector retrieval and lexical/exact-term retrieval and SHALL combine their ranked results into one inspectable result list.

#### Scenario: A paraphrased query is submitted
- **WHEN** the query uses wording different from the source document
- **THEN** semantic retrieval can surface a relevant section even when the exact phrase is absent

#### Scenario: An exact version or term is submitted
- **WHEN** the query includes a distinctive version, date, title, or product term
- **THEN** lexical or exact-term retrieval can contribute a matching result even if semantic similarity is not the strongest signal

### Requirement: Search SHALL support metadata filters
The system SHALL allow callers to constrain retrieval by available metadata such as category, status, version, or source path.

#### Scenario: A user requests current billing guidance
- **WHEN** the query includes a current-status and billing-category filter
- **THEN** archived non-billing sections are excluded before the final results are returned

### Requirement: Search SHALL make ranking behavior inspectable
The response SHALL expose enough information to understand whether a result came from semantic retrieval, lexical retrieval, or both, without exposing embeddings or credentials.

#### Scenario: A user compares retrieval approaches
- **WHEN** a result is returned by both retrieval methods
- **THEN** the response identifies its component ranks or equivalent diagnostic fields and its final combined rank

### Requirement: Search SHALL handle empty or low-evidence queries safely
The system SHALL return an empty result or an explicit low-evidence response when no indexed section meets the retrieval conditions and SHALL not fabricate a document result.

#### Scenario: A query concerns an unsupported topic
- **WHEN** no indexed section is relevant to the query
- **THEN** the response indicates that no supporting document evidence was found
