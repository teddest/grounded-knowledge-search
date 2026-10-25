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
