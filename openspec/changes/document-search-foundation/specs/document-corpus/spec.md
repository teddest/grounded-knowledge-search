## ADDED Requirements

### Requirement: The repository SHALL include a reproducible educational document corpus
The repository SHALL include a fictional corpus of policies, procedures, product guidance, support information, and operational documents that can be indexed without additional private data.

#### Scenario: A new user inspects the corpus
- **WHEN** a user clones the repository
- **THEN** the user can identify the document directories and understand the subject areas covered without creating documents first

### Requirement: Corpus documents SHALL expose searchable metadata
Each corpus document SHALL include enough metadata to distinguish its title, stable identifier, category, status, version, effective date, audience, and owner when those concepts apply.

#### Scenario: An ingestion process reads document metadata
- **WHEN** a supported corpus document is parsed
- **THEN** its metadata is available for indexing and filtering alongside its text sections

### Requirement: The corpus SHALL include version and authority cases
The corpus SHALL include at least one historical/current document pair and questions that test current-version preference, historical lookup, and conflicting guidance.

#### Scenario: A user evaluates version-sensitive retrieval
- **WHEN** the user asks for the current rule and a historical rule exists
- **THEN** the evaluation data identifies the current source as the expected source for the current question and the historical source for the historical question

### Requirement: The repository SHALL include labeled evaluation questions
The repository SHALL include representative questions with use-case labels, expected source paths, and expected answer summaries covering direct lookup, paraphrase, multi-document retrieval, version comparison, and unsupported or ambiguous requests.

#### Scenario: An evaluator loads the labeled questions
- **WHEN** the evaluation workflow reads the question file
- **THEN** each case contains a query and at least one expected source that can be used for retrieval scoring
