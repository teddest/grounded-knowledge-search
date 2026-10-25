## ADDED Requirements

### Requirement: Node dependencies SHALL use pnpm and a committed lockfile
The monorepo SHALL use pnpm for Node.js workspace installation and SHALL commit the resulting lockfile. Automated and containerized installs SHALL use frozen or equivalent lockfile-enforcing behavior.

#### Scenario: A clean environment installs Node dependencies
- **WHEN** the documented installation command runs
- **THEN** pnpm installs the versions recorded in the lockfile and fails if the manifest and lockfile disagree

### Requirement: Python dependencies SHALL use a locked resolver workflow
The Python API SHALL use a supported locked dependency workflow with a committed lockfile and SHALL fail or require an explicit update when dependency declarations and the lockfile disagree.

#### Scenario: A clean environment installs Python dependencies
- **WHEN** the documented Python installation command runs
- **THEN** it resolves from the committed lockfile without silently selecting new package versions

### Requirement: Package registries SHALL be explicit
Node and Python package configuration SHALL identify the intended public registries and SHALL not silently use unreviewed alternate registries or repository-local package shadowing.

#### Scenario: A package installation runs in Docker
- **WHEN** the package manager resolves dependencies
- **THEN** it uses the configured registry policy and the installation configuration does not contain credentials

### Requirement: Lifecycle and build scripts SHALL be controlled
Dependency installation SHALL disable or explicitly allowlist package lifecycle/build scripts, and any required exception SHALL be documented and reviewed.

#### Scenario: A new dependency requires an install script
- **WHEN** the dependency is added to the project
- **THEN** the change identifies the script, explains why it is needed, and adds it to the reviewed allowlist rather than enabling all install scripts

### Requirement: Dependency updates SHALL be auditable
Dependency updates SHALL be performed as intentional changes that include lockfile diffs and SHALL run the available vulnerability and license checks before acceptance.

#### Scenario: A dependency version is updated
- **WHEN** a contributor changes a direct or transitive dependency
- **THEN** the review includes the manifest/lockfile change and the relevant security-check result or documented limitation

### Requirement: Dependency sources SHALL be constrained
Dependencies SHALL NOT use unpinned Git repositories, arbitrary URLs, local path shadowing, or package names that are not justified by the application without documented review.

#### Scenario: A contributor proposes a Git dependency
- **WHEN** a dependency cannot be sourced from the configured registry
- **THEN** the change documents the source, version or commit pin, reason, and supply-chain review before it is accepted

### Requirement: Secrets SHALL be excluded from package configuration and logs
Package-manager tokens, registry credentials, OpenRouter keys, and other secrets SHALL be supplied through the environment or secret manager and SHALL not appear in manifests, lockfiles, Docker layers, logs, or test fixtures.

#### Scenario: Installation fails with an authentication error
- **WHEN** the package manager reports an authentication failure
- **THEN** the application and CI logs redact credentials and the repository contains no replacement token or secret configuration

### Requirement: Supply-chain checks SHALL be part of the repeatable quality workflow
The repository SHALL provide a repeatable command for lockfile validation and available Python/Node dependency security checks, and the result SHALL be visible in the documented verification workflow.

#### Scenario: A dependency has a known high-severity advisory
- **WHEN** the security check runs
- **THEN** the check reports the affected dependency and fails or requires an explicit documented exception before acceptance
