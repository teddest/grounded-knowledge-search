## ADDED Requirements

### Requirement: The answer workflow SHALL use retrieved evidence
The system SHALL generate an answer only after retrieving document sections and SHALL provide the retrieved source records alongside the generated answer.

#### Scenario: A user asks how to handle a failed payment
- **WHEN** the answer workflow runs
- **THEN** the model receives bounded sections from the indexed corpus and the response includes those source sections for inspection

### Requirement: Generated answers SHALL cite source sections
The answer prompt and response format SHALL require citations that map to stable source result numbers, paths, headings, or locations returned by the search workflow.

#### Scenario: An answer contains a policy claim
- **WHEN** the model makes a claim supported by retrieved context
- **THEN** the claim includes a citation that a user can map to a returned source section

### Requirement: The answer workflow SHALL acknowledge insufficient evidence
The system SHALL instruct the model not to invent policy, product behavior, or document references and SHALL return an explicit uncertainty statement when the retrieved evidence does not support an answer.

#### Scenario: The user asks about an undocumented rule
- **WHEN** retrieval returns no sufficient supporting section
- **THEN** the answer states that the available documents do not establish the requested rule

### Requirement: The answer workflow SHALL preserve source authority context
The answer context SHALL include relevant metadata such as status, version, and effective date so the model can distinguish current and historical guidance.

#### Scenario: Current and archived policy sections are retrieved
- **WHEN** the question asks for the current rule
- **THEN** the answer can identify the current source and avoid presenting an archived source as the current policy without qualification

### Requirement: External model configuration SHALL be explicit
The answer workflow SHALL use a configurable OpenRouter chat model and SHALL fail clearly when required credentials or model configuration are missing.

#### Scenario: The chat provider is not configured
- **WHEN** a user requests an answer without an OpenRouter key
- **THEN** the application returns a configuration error and does not present an invented answer
