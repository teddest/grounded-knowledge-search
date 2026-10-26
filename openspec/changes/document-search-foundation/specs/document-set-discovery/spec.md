## ADDED Requirements

### Requirement: The API SHALL discover corpus document sets
The system SHALL discover the default corpus directory and supported immediate child directories that contain supported documents, while excluding repository and tooling directories.

#### Scenario: The corpus contains category directories
- **WHEN** the discovery endpoint runs against `documents/`
- **THEN** it returns the `All documents` set and supported category sets such as policies, procedures, product, support, and operations

### Requirement: Discovery SHALL be idempotent
Repeated discovery SHALL reuse existing registrations for the same root path rather than creating duplicate document sets.

#### Scenario: Discovery runs twice
- **WHEN** the user refreshes document-set discovery
- **THEN** each discovered root path has one stable registration and the list remains duplicate-free

### Requirement: Discovery SHALL preserve custom document sets
User-registered document sets outside the default corpus categories SHALL remain available after discovery runs.

#### Scenario: A user registers a custom folder
- **WHEN** discovery runs after the custom folder has been registered
- **THEN** the custom document set remains in the returned document-set list

### Requirement: The web interface SHALL expose discovered document sets
The web interface SHALL refresh document-set discovery when loading the workspace and SHALL select the default `All documents` set when no prior selection exists.

#### Scenario: A user opens the workspace
- **WHEN** the corpus contains discoverable category directories
- **THEN** the document-set selector lists the default set and discovered categories without requiring manual API calls

### Requirement: The web interface SHALL support custom document-set registration
The interface SHALL provide a labeled name/path form or equivalent action that validates a custom path through the API and adds the resulting document set to the selector.

#### Scenario: A user registers a custom folder
- **WHEN** the user submits a valid name and repository-relative path
- **THEN** the document set is created, selected, and available for ingestion

#### Scenario: A user submits an invalid path
- **WHEN** the API rejects the path
- **THEN** the interface displays an actionable error without losing the existing document-set selection
