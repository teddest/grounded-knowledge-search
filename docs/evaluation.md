# Evaluation guide

The evaluation workflow measures retrieval separately from answer generation. A relevant result does not prove that a generated answer is correct or that a citation supports the claim.

## Labeled questions

The checked-in `evaluation-queries.json` contains representative questions with:

- Query ID
- Query text
- Use case
- Expected source paths
- Optional expected answer summary

The source paths are matched against the returned section source paths. Matching allows a document-set-relative path to match a repository-relative path, but different document versions remain different sources.

## Metrics

### Hit@K

The percentage of queries where at least one expected source appears in the first `K` results.

Useful for:

> Did the user find any useful evidence?

### Precision@K

The proportion of the first `K` results that match an expected source.

```text
Precision@5 = relevant results in top 5 / 5
```

This exposes noise even when the correct source is present.

### Recall@K

The proportion of expected sources that appear in the first `K` results.

This is especially useful for questions that require multiple documents.

### MRR

Mean Reciprocal Rank measures the position of the first relevant result:

```text
rank 1 -> 1.0
rank 2 -> 0.5
rank 5 -> 0.2
```

## Running an evaluation

1. Start the stack.
2. Register the `documents` directory or the repository root if you are intentionally testing broader discovery.
3. Ingest the document set.
4. Generate embeddings.
5. Submit the labeled cases to `/api/v1/evaluate`.

The complete quality workflow includes the unit tests and static checks:

```bash
./scripts/check.sh
```

## Baseline

`evaluation-baseline.json` records the measured baseline for the checked-in synthetic corpus and questions. It includes the embedding model, `K`, query count, metrics, interpretation, and limitations.

The baseline is not a production claim. It changes when any of the following change:

- Corpus contents
- Chunking behavior
- Embedding model
- Metadata filters
- Candidate count
- Fusion settings
- Evaluation source-matching rules

## Failure analysis

Use per-query results to categorize failures:

- Relevant source absent from top K
- Correct concept but wrong document version
- Exact term missed
- Lexical result outranking a better semantic result
- Semantic result too broad or unrelated
- Too many sections from the same document
- Missing metadata filter
- Stale or incomplete index
- Citation source retrieved but not used correctly in the answer

## Human review

Retrieval metrics cannot evaluate everything. Review answer quality separately for:

- Citation correctness
- Evidence support
- Completeness
- Handling of conflicting sources
- Appropriate uncertainty
- Whether the answer invents unsupported details
