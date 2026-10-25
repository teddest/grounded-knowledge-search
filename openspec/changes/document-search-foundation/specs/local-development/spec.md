## ADDED Requirements

### Requirement: The monorepo SHALL run locally with one development command
A new user SHALL be able to start the Next.js web application, Python API, and PostgreSQL/pgvector dependency with one documented development script.

#### Scenario: A user starts from a fresh clone
- **WHEN** the user provides the documented environment configuration and runs the development script
- **THEN** the database, API, and web application start with a health-checkable local endpoint

### Requirement: Local development SHALL provide web hot reload
The development runtime SHALL bind-mount the web source and run the Next.js development server so supported UI edits are reflected without rebuilding the container.

#### Scenario: A user edits a web component
- **WHEN** the user saves a change to a Next.js or Tailwind source file
- **THEN** the running web application reloads or refreshes without requiring a manual image rebuild

### Requirement: Local development SHALL provide API reload
The development runtime SHALL run the Python API with a development reload mode for supported source changes.

#### Scenario: A user edits an API module
- **WHEN** the user saves a change to a Python API source file
- **THEN** the API process reloads or restarts through the development runtime without restarting the database manually

### Requirement: Model configuration SHALL be environment-based
The system SHALL read the OpenRouter API key, embedding model, chat model, database connection, and document location from environment configuration rather than requiring source edits.

#### Scenario: A user selects different OpenRouter models
- **WHEN** the user changes the model environment variables and restarts the application
- **THEN** subsequent embedding and answer requests use the configured models

### Requirement: Local setup SHALL include a safe example configuration
The repository SHALL include an example environment file without real credentials and SHALL document that indexed document content may be sent to OpenRouter.

#### Scenario: A user inspects configuration before running the app
- **WHEN** the user reads the example environment file and setup guide
- **THEN** the user can identify required secrets, model settings, vector dimensions, and external data-handling implications

### Requirement: The application SHALL expose a health check
The API SHALL provide a health check that reports API availability and database connectivity without requiring a model request, and the web application SHALL expose a usable status surface for that check.

#### Scenario: The database is unavailable
- **WHEN** a user calls the health endpoint
- **THEN** the response indicates an unhealthy dependency instead of reporting the system as ready

### Requirement: Educational documentation SHALL explain the system boundaries
The repository SHALL explain the data flow, supported inputs, retrieval stages, answer-generation limitations, evaluation workflow, and known non-goals.

#### Scenario: A reader wants to learn how retrieval works
- **WHEN** the reader follows the repository documentation
- **THEN** the reader can run the system and identify which behavior belongs to ingestion, retrieval, answer generation, and evaluation
