from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import PurePosixPath
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, Field

from .retrieval import SearchFilters, SearchResult


class EvaluationCase(BaseModel):
    id: str
    query: str = Field(min_length=1)
    use_case: str | None = None
    relevant_sources: list[str] = Field(min_length=1)
    expected_answer: str | None = None
    filters: SearchFilters = Field(default_factory=SearchFilters)


class EvaluationCaseResult(BaseModel):
    id: str
    query: str
    hit_at_k: int
    precision_at_k: float
    recall_at_k: float
    reciprocal_rank: float
    expected_sources: list[str]
    matched_sources: list[str]
    returned_sources: list[str]
    results: list[SearchResult]


class EvaluationMetrics(BaseModel):
    hit_at_k: float
    precision_at_k: float
    recall_at_k: float
    mrr: float


class EvaluationReport(BaseModel):
    k: int
    query_count: int
    metrics: EvaluationMetrics
    cases: list[EvaluationCaseResult]


class EvaluationRetriever(Protocol):
    def search(
        self,
        document_set_id: UUID,
        query: str,
        filters: SearchFilters | None = None,
        limit: int = 10,
    ) -> list[SearchResult]: ...


def _normalize_path(path: str) -> str:
    return PurePosixPath(path.strip().lstrip("./")).as_posix()


def source_matches(returned_path: str, expected_path: str) -> bool:
    returned = _normalize_path(returned_path)
    expected = _normalize_path(expected_path)
    return (
        returned == expected
        or returned.endswith(f"/{expected}")
        or expected.endswith(f"/{returned}")
    )


def _matching_sources(results: Sequence[SearchResult], expected: Sequence[str]) -> list[str]:
    return [
        result.source_path
        for result in results
        if any(source_matches(result.source_path, expected_path) for expected_path in expected)
    ]


def evaluate_case(
    retriever: EvaluationRetriever,
    document_set_id: UUID,
    case: EvaluationCase,
    k: int,
) -> EvaluationCaseResult:
    results = retriever.search(document_set_id, case.query, case.filters, k)
    matched_sources = _matching_sources(results, case.relevant_sources)
    matched_flags = [
        source in matched_sources for source in [result.source_path for result in results]
    ]
    first_match = next((index + 1 for index, matched in enumerate(matched_flags) if matched), None)
    matched_expected = {
        expected
        for expected in case.relevant_sources
        if any(source_matches(result.source_path, expected) for result in results)
    }
    return EvaluationCaseResult(
        id=case.id,
        query=case.query,
        hit_at_k=int(first_match is not None),
        precision_at_k=len(matched_sources) / k,
        recall_at_k=len(matched_expected) / len(case.relevant_sources),
        reciprocal_rank=1 / first_match if first_match else 0.0,
        expected_sources=case.relevant_sources,
        matched_sources=matched_sources,
        returned_sources=[result.source_path for result in results],
        results=results,
    )


def evaluate_cases(
    retriever: EvaluationRetriever,
    document_set_id: UUID,
    cases: Iterable[EvaluationCase],
    k: int = 5,
) -> EvaluationReport:
    if k < 1:
        raise ValueError("k must be greater than zero")
    case_results = [evaluate_case(retriever, document_set_id, case, k) for case in cases]
    if not case_results:
        raise ValueError("at least one evaluation case is required")
    count = len(case_results)
    return EvaluationReport(
        k=k,
        query_count=count,
        metrics=EvaluationMetrics(
            hit_at_k=sum(case.hit_at_k for case in case_results) / count,
            precision_at_k=sum(case.precision_at_k for case in case_results) / count,
            recall_at_k=sum(case.recall_at_k for case in case_results) / count,
            mrr=sum(case.reciprocal_rank for case in case_results) / count,
        ),
        cases=case_results,
    )
