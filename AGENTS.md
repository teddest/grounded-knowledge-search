# Agent and contributor instructions

These instructions apply to the entire repository.

## Project purpose

Grounded Knowledge Search is an educational document-search application. It demonstrates document ingestion, semantic and lexical retrieval, grounded answers, citations, and evaluation using the checked-in Northstar Relay dataset.

Keep the implementation understandable to a reader learning search systems. Prefer small, explicit modules over opaque abstractions and unnecessary framework complexity.

## Non-negotiable Git workflow

- **Never work directly on `main`.** Do not edit files, create commits, or push commits while checked out on `main`.
- **Never commit directly to `main`.** Every change must be made on a topic branch and merged through a pull request.
- Before starting work, synchronize the local base without making changes on it:

  ```bash
  git fetch origin
  git switch main
  git pull --ff-only origin main
  git switch -c <branch-type>/<short-description>
  ```

- Branch names must use one of these prefixes:
  - `feat/` for new behavior
  - `fix/` for bug fixes
  - `docs/` for documentation-only changes
  - `test/` for test-only changes
  - `chore/` for tooling or maintenance
- Keep each branch focused on one OpenSpec task group or one closely related documentation change.
- Before opening a PR, rebase the topic branch onto the latest `origin/main` when necessary. Resolve conflicts on the topic branch and use `git push --force-with-lease` only for that topic branch after a rebase.
- Never force-push, reset, or rewrite `main`.
- Do not merge locally. Open a GitHub pull request for review and use the merge policy below.
- Require at least one approval and passing verification before merging.
- Use **Squash and merge** for completed branches so each task group becomes one focused commit on `main`.
- Do not use merge commits for ordinary task branches.
- Delete the remote topic branch after a successful merge.

## OpenSpec workflow

This repository uses [OpenSpec](https://github.com/Fission-AI/OpenSpec). Install or otherwise make the OpenSpec CLI available before working with the proposal, specs, or task checklist.

- Read the applicable proposal, design, specs, and tasks before implementation.
- Use one branch and pull request per task group whenever practical.
- Update the OpenSpec task checklist as work is completed.
- If implementation changes the agreed behavior, update the OpenSpec artifacts in the same or a preceding PR rather than silently changing scope.
- Do not begin a large implementation task until its requirement and acceptance scenarios are clear.

## Implementation standards

### Python API

- Use `uv` for Python dependency resolution and keep production Python configuration in `pyproject.toml`; verify the supported Python version before selecting dependencies.
- Use type hints for public functions and strict static checking where practical; avoid `Any` and untyped boundary data.
- Keep HTTP/Pydantic schemas, domain logic, persistence, and provider adapters in separate modules.
- Use FastAPI dependency injection for database sessions and external providers rather than constructing clients inside route handlers.
- Use ports/adapters or narrow interfaces at the database and OpenRouter boundaries so domain and unit tests do not require network access.
- Prefer small pure functions for parsing, ranking, metrics, and formatting. Use classes when state, lifecycle, or an explicit interface makes them clearer.
- Use explicit exception types and translate internal failures into stable API errors; never use bare `except` blocks.
- Use the project formatter, linter, type checker, pytest, and branch coverage checks on every relevant change.

### Node.js tooling and services

- Use pnpm for the Node.js workspace. Verify and pin the supported Node.js LTS and pnpm versions; commit the lockfile and use the same toolchain locally and in Docker.
- Use `package.json` scripts as the canonical interface for development, linting, type checking, testing, coverage, and builds.
- Prefer ESM modules, explicit imports, and small modules with one responsibility; avoid putting application logic in ad hoc build or shell scripts.
- Validate environment variables at process startup and keep configuration separate from business logic.
- Handle asynchronous operations explicitly, propagate errors with context, and do not leave unhandled promise rejections.
- Keep Node-specific adapters and tooling separate from domain behavior so they can be tested without starting a server.

### TypeScript and Next.js

- Use strict TypeScript and avoid `any`, non-null assertions, and unchecked type casts unless the reason is documented.
- Use the App Router and server components by default; add client components only for browser interactivity or client-side state.
- Keep API calls in typed client modules rather than scattering raw `fetch` calls across components.
- Keep presentation components focused and composable; keep retrieval, ranking, and answer-generation logic in the Python API.
- Validate untrusted API responses at the boundary when generated types alone are insufficient.
- Use accessible semantic HTML, keyboard-accessible controls, and explicit loading, empty, error, and retry states.
- Use the project ESLint, formatter, TypeScript, unit/component, and Playwright checks.

### SQL, Docker, and shell

- Use versioned database migrations, parameterized SQL, explicit transactions, foreign keys, and indexes justified by query behavior.
- Avoid `SELECT *` in application queries and inspect query plans for retrieval-critical queries.
- Keep Docker images and base dependencies pinned or lockfile-controlled, expose health checks, and avoid putting secrets in images or layers.
- Shell scripts must use `set -Eeuo pipefail`, quote variables, validate required tools/configuration, and be safe to rerun.
- Prefer documented, testable commands over manual multi-terminal setup.

### Package supply-chain security

- Commit and enforce `pnpm-lock.yaml` and `uv.lock`; use frozen/locked installs in Docker and automated checks.
- Use explicit, reviewed package registries. Do not add unpinned Git, arbitrary URL, local-path, or shadowed dependencies without documenting the reason and review.
- Disable package lifecycle/build scripts by default where possible; explicitly allowlist only the scripts required by reviewed dependencies.
- Run available Node and Python dependency vulnerability/audit checks, and review lockfile diffs for every dependency update.
- Keep dependency versions, package-manager versions, and registry configuration reproducible; do not rely on a developer's global setup.
- Never commit package-manager tokens, registry credentials, API keys, or generated files containing secrets.

### Cross-cutting design patterns

- Use dependency inversion only at real boundaries such as databases, model providers, clocks, and file systems; do not add abstractions without a testability or replacement benefit.
- Prefer composition and explicit data flow over global state, hidden singletons, and framework magic.
- Keep external side effects at the edges and make core behavior deterministic where possible.
- Treat framework defaults as hypotheses to verify against official documentation, not assumptions.

- Preserve document metadata, source locations, version status, and effective dates.
- Keep retrieval evidence separate from generated answers.
- Never present an answer as supported when the indexed evidence is insufficient.
- Keep OpenRouter credentials, document content, and sensitive request data out of logs.
- Use synthetic or non-sensitive documents for examples and tests.
- Add tests for new behavior and update educational documentation when user-visible behavior changes.
- Do not claim measured relevance, latency, cost, or scale without recorded evidence.

## Pull request expectations

Every PR must:

1. Be based on a topic branch, never `main`.
2. Identify the OpenSpec task group it implements, if applicable.
3. Explain the behavior changed and the verification performed.
4. Include tests or a clear reason tests are not applicable.
5. Keep unrelated formatting, refactoring, and generated files out of the PR.
6. Pass the documented checks and receive the required review before merging.
