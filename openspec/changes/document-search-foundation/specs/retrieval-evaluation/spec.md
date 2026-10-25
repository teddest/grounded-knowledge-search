## ADDED Requirements

### Requirement: Evaluation SHALL use the same retrieval path as the application
The evaluation workflow SHALL submit labeled questions through the application retrieval implementation rather than using a separate test-only ranking implementation.

#### Scenario: A baseline evaluation is run
- **WHEN** the evaluator loads the checked-in labeled questions
- **THEN** it invokes the same search behavior used by interactive users and records the returned evidence

### Requirement: Evaluation SHALL report top-k retrieval metrics
The evaluator SHALL report Hit@K, Precision@K, Recall@K, and Mean Reciprocal Rank across the labeled cases, with the selected K visible in the output.

#### Scenario: An evaluation contains 22 labeled questions
- **WHEN** the evaluator completes
- **THEN** the report includes aggregate metric values, query count, K, and per-query results or failure details

### Requirement: Evaluation SHALL make source matching rules explicit
The evaluator SHALL document or encode how returned source paths are matched against expected sources and SHALL avoid silently treating unrelated sections as correct.

#### Scenario: A result comes from the wrong document version
- **WHEN** the expected source is the current policy and the returned source is only the archived policy
- **THEN** the evaluator can identify the mismatch rather than counting the result as an unqualified source hit

### Requirement: Evaluation SHALL support failure analysis
The evaluation output SHALL retain enough per-query information to inspect missed, noisy, and incorrectly ranked results.

#### Scenario: A query has no expected source in the top K
- **WHEN** the evaluator reports the case
- **THEN** it includes the query, expected sources, returned sources, and metric contribution so the failure can be categorized

### Requirement: Citation quality SHALL remain distinct from retrieval quality
The evaluation documentation SHALL distinguish whether a relevant source was retrieved from whether a generated answer correctly used and cited that source.

#### Scenario: Retrieval succeeds but an answer cites the wrong section
- **WHEN** a reviewer assesses the answer
- **THEN** retrieval metrics are not treated as proof of citation correctness, and the citation issue can be recorded separately
