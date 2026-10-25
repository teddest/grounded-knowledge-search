# Contributing

Grounded Knowledge Search uses a pull-request-only workflow. `main` is the protected integration branch and must always remain in a runnable, reviewable state.

## Branching strategy

### 1. Synchronize the base branch

Do this before starting a task. Synchronizing `main` is the only time contributors should check it out; do not edit or commit there.

```bash
git fetch origin
git switch main
git pull --ff-only origin main
```

### 2. Create a focused topic branch

```bash
git switch -c feat/hybrid-retrieval
```

Use one of these prefixes:

| Prefix | Use |
|---|---|
| `feat/` | New application behavior |
| `fix/` | A bug fix |
| `docs/` | Documentation-only work |
| `test/` | Test-only work |
| `chore/` | Tooling, configuration, or maintenance |

Branch names should be short, lowercase, and describe the change. The planned implementation branches are listed in `openspec/changes/document-search-foundation/tasks.md`.

### 3. Keep the branch focused

A branch should implement one task group or one small, coherent change. Avoid combining unrelated features, formatting, or refactors. If the scope changes, update the relevant OpenSpec artifacts before expanding the implementation.

### 4. Rebase before opening or updating a PR

```bash
git fetch origin
git rebase origin/main
```

Resolve conflicts on the topic branch, run the checks again, and update the branch with:

```bash
git push --force-with-lease origin <branch-name>
```

`--force-with-lease` is permitted only on the contributor's topic branch after a rebase. Never use it on `main`.

## Pull request strategy

Every change must be merged through a GitHub pull request. Direct pushes to `main` are not allowed.

A PR should include:

- A concise description of the behavior or documentation change
- The relevant OpenSpec task group or requirement
- Tests and verification commands that were run
- Known limitations or follow-up work
- Any changes to configuration or external model behavior

Keep PRs small enough for one reviewer to understand. Prefer the branch boundaries in the OpenSpec task plan:

1. Runtime foundation
2. Document model and ingestion
3. OpenRouter embeddings and indexing
4. Hybrid retrieval
5. Grounded answers
6. Retrieval evaluation
7. Learning interface
8. Educational documentation

## Review and merge strategy

- At least one reviewer must approve the PR.
- Required checks must pass before merging.
- Reviewers should verify behavior against the relevant OpenSpec scenarios, not only inspect implementation style.
- Use **Squash and merge** for completed PRs so each branch becomes one focused commit on `main`.
- Do not use merge commits for ordinary feature branches.
- Delete the remote topic branch after a successful merge.
- Start the next task from the updated `origin/main`, not from an old topic branch.

## Local verification

Run the checks relevant to the change before requesting review. At minimum:

```bash
openspec validate document-search-foundation
```

As the application is implemented, the README will define the test, lint, type-check, and Docker verification commands that must also pass.

## Security and data handling

- Never commit `.env` files, API keys, or credentials.
- Treat document content sent to OpenRouter as externally processed data.
- Use the synthetic Northstar Relay dataset for examples unless a change explicitly documents another safe data source.
- Do not include secrets or sensitive document content in logs, screenshots, fixtures, or pull-request descriptions.
