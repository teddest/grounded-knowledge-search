## ADDED Requirements

### Requirement: The Python service SHALL have automated unit and API tests
The Python application SHALL use pytest-based tests for domain logic, ingestion, retrieval, evaluation, error handling, and HTTP endpoints. External model providers and database boundaries SHALL be replaceable with deterministic test doubles.

#### Scenario: Tests run without an OpenRouter key
- **WHEN** the Python test suite runs in a clean environment
- **THEN** unit and API tests complete without making external model requests

### Requirement: The web application SHALL have typed component and integration tests
The TypeScript application SHALL use a framework-compatible unit/component test runner and React Testing Library for components and client behavior. Tests SHALL cover successful, loading, empty, error, and citation states.

#### Scenario: A search result component is tested
- **WHEN** the component receives a result, no-result state, and API-error state
- **THEN** tests verify the accessible content and available user action for each state

### Requirement: The primary user flow SHALL have browser-level coverage
The project SHALL include a Playwright or equivalent browser test for the primary flow from application load through search and source inspection, with answer-generation behavior tested using a deterministic backend fixture or stub.

#### Scenario: A user searches and inspects evidence
- **WHEN** the browser test loads the application, submits a query, and opens a result
- **THEN** the test verifies that ranked evidence and source metadata are visible to the user

### Requirement: Coverage SHALL include branch coverage and enforce a near-complete threshold
The Python and TypeScript test commands SHALL produce separate line, function, statement, and branch coverage reports. The quality gate SHALL target 100% coverage for deterministic first-party application logic and SHALL fail when the agreed repository threshold is not met.

#### Scenario: A new branch is introduced without a test
- **WHEN** the coverage checks run
- **THEN** the quality gate identifies the uncovered branch and prevents the change from being treated as verified

### Requirement: Coverage exclusions SHALL be explicit and minimal
Generated files, framework bootstrap code, configuration-only files, and external vendor code MAY be excluded only through documented coverage configuration. Application logic SHALL NOT be excluded merely to raise the reported percentage.

#### Scenario: A contributor adds a coverage exclusion
- **WHEN** a source path is excluded from coverage
- **THEN** the change documents why the path is non-testable or generated and does not hide domain behavior

### Requirement: Static checks SHALL run for both application languages
The repository SHALL provide repeatable commands for Python formatting/linting/type checking and TypeScript formatting/linting/type checking/build validation.

#### Scenario: A type error is introduced in the web client
- **WHEN** the quality checks run
- **THEN** the TypeScript check fails before the change is considered ready

### Requirement: API contracts SHALL be tested across the service boundary
The project SHALL test that the TypeScript client models and the FastAPI response shapes agree for ingestion status, search results, and grounded answers.

#### Scenario: The API response shape changes
- **WHEN** a response field required by the web client is removed or renamed
- **THEN** a contract or type-check test fails and identifies the mismatch
