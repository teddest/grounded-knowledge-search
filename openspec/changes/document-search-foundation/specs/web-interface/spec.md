## ADDED Requirements

### Requirement: The web interface SHALL use Next.js, TypeScript, and Tailwind CSS
The browser application SHALL use the Next.js App Router, TypeScript, and Tailwind CSS through the official current Next.js integration. Framework and dependency versions SHALL be verified against official documentation during implementation and committed in lockfiles.

#### Scenario: A reader inspects the web application
- **WHEN** the reader opens the web application source
- **THEN** the routing, components, and styles are identifiable as a typed Next.js App Router application using Tailwind CSS

### Requirement: The web interface SHALL expose document-set status and ingestion
The interface SHALL show the available document set, indexing status, and actionable progress or failure information.

#### Scenario: A user opens the application before indexing
- **WHEN** the API has a registered but unindexed document set
- **THEN** the interface shows that indexing is required and provides a way to start or retry indexing

### Requirement: The web interface SHALL support hybrid search interactions
The interface SHALL allow a user to submit a natural-language query, select supported metadata filters, and inspect ranked results with source paths, headings, status, version, and excerpts.

#### Scenario: A user searches for current billing guidance
- **WHEN** the user submits a query with a current-status filter
- **THEN** the interface displays ranked matching sections and the metadata used to interpret source authority

### Requirement: The web interface SHALL display grounded answers and citations
The interface SHALL display the generated answer separately from its supporting source records and SHALL make each citation traceable to a returned document section.

#### Scenario: A user asks how to handle a failed payment
- **WHEN** the answer service returns a cited response
- **THEN** the interface displays the answer, citation markers, and the corresponding source excerpts or source details

### Requirement: The web interface SHALL handle loading, empty, and failure states
The interface SHALL provide accessible loading indicators, no-result messaging, provider-configuration errors, API errors, and retry actions where retry is meaningful.

#### Scenario: Search returns no evidence
- **WHEN** the API returns no matching sections
- **THEN** the interface explains that no supporting evidence was found instead of displaying an empty or misleading answer

### Requirement: The web interface SHALL provide an educational About page
The application SHALL provide a discoverable About page that explains the system purpose, architecture, document-to-answer data flow, technology choices, evaluation approach, limitations, and external model data-handling considerations.

#### Scenario: A reader opens the About page
- **WHEN** the reader navigates to the About page
- **THEN** the page presents the major system concepts in accessible, readable sections without requiring a configured model key

### Requirement: The frontend SHALL keep application logic separated from presentation
The web application SHALL use typed API-client functions, reusable presentational components, and explicit client/server boundaries. Retrieval, ranking, embedding, and answer-generation logic SHALL remain in the Python API.

#### Scenario: A UI component renders search results
- **WHEN** the component receives a typed result model
- **THEN** it renders the model without implementing a second ranking or retrieval algorithm in the browser
