from __future__ import annotations

from uuid import uuid4

import pytest

from grounded_knowledge_api.evaluation import (
    EvaluationCase,
    evaluate_case,
    evaluate_cases,
    source_matches,
)
from grounded_knowledge_api.retrieval import SearchResult


def result(identifier: int, source_path: str) -> SearchResult:
    return SearchResult(
        id=identifier,
        source_path=source_path,
        title="Policy",
        content="Evidence",
        heading_path=[],
        fusion_score=0.1,
    )


class Retriever:
    def __init__(self, results):
        self.results = results

    def search(self, *_args, **_kwargs):
        return self.results


def case(*sources: str) -> EvaluationCase:
    return EvaluationCase(id="q1", query="question", relevant_sources=list(sources))


def test_source_matching_handles_relative_and_nested_paths():
    assert source_matches("policies/refunds-2025.md", "refunds-2025.md")
    assert source_matches("refunds-2025.md", "policies/refunds-2025.md")
    assert source_matches("./refunds-2025.md", "refunds-2025.md")
    assert not source_matches("refunds-2024.md", "refunds-2025.md")


def test_evaluate_case_reports_ranking_and_source_matches():
    retriever = Retriever([result(1, "policies/refunds-2025.md"), result(2, "policies/other.md")])

    evaluated = evaluate_case(retriever, uuid4(), case("refunds-2025.md"), 5)

    assert evaluated.hit_at_k == 1
    assert evaluated.precision_at_k == 0.2
    assert evaluated.recall_at_k == 1.0
    assert evaluated.reciprocal_rank == 1.0
    assert evaluated.matched_sources == ["policies/refunds-2025.md"]


def test_evaluate_case_reports_miss():
    evaluated = evaluate_case(
        Retriever([result(1, "refunds-2024.md")]), uuid4(), case("refunds-2025.md"), 5
    )

    assert evaluated.hit_at_k == 0
    assert evaluated.recall_at_k == 0
    assert evaluated.reciprocal_rank == 0


def test_evaluate_cases_aggregates_metrics():
    cases = [
        case("refunds-2025.md"),
        EvaluationCase(id="q2", query="q2", relevant_sources=["other.md"]),
    ]
    report = evaluate_cases(Retriever([result(1, "refunds-2025.md")]), uuid4(), cases, k=5)

    assert report.query_count == 2
    assert report.metrics.hit_at_k == 0.5
    assert len(report.cases) == 2


def test_evaluate_cases_validates_inputs():
    retriever = Retriever([])
    with pytest.raises(ValueError, match="greater than zero"):
        evaluate_cases(retriever, uuid4(), [case("source.md")], 0)
    with pytest.raises(ValueError, match="at least one"):
        evaluate_cases(retriever, uuid4(), [], 5)
