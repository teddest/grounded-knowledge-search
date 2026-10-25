from __future__ import annotations

from datetime import date
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, Field

from .config import Settings
from .embeddings import EmbeddingProvider


class RetrievalStore(Protocol):
    def vector_search(
        self,
        document_set_id: UUID,
        embedding: list[float],
        limit: int,
        category: str | None = None,
        status: str | None = None,
        version: str | None = None,
    ) -> list[dict[str, Any]]: ...

    def lexical_search(
        self,
        document_set_id: UUID,
        query: str,
        limit: int,
        category: str | None = None,
        status: str | None = None,
        version: str | None = None,
    ) -> list[dict[str, Any]]: ...


class SearchFilters(BaseModel):
    category: str | None = None
    status: str | None = None
    version: str | None = None


class SearchResult(BaseModel):
    id: int
    source_path: str
    title: str
    category: str | None = None
    status: str | None = None
    version: str | None = None
    effective_date: date | None = None
    heading_path: list[str] = Field(default_factory=list)
    start_line: int | None = None
    end_line: int | None = None
    content: str
    similarity: float | None = None
    lexical_score: float | None = None
    vector_rank: int | None = None
    lexical_rank: int | None = None
    fusion_score: float


class HybridRetriever:
    def __init__(
        self, store: RetrievalStore, provider: EmbeddingProvider, settings: Settings
    ) -> None:
        self.store = store
        self.provider = provider
        self.settings = settings

    def search(
        self,
        document_set_id: UUID,
        query: str,
        filters: SearchFilters | None = None,
        limit: int = 10,
    ) -> list[SearchResult]:
        if not query.strip():
            raise ValueError("query must not be empty")
        if limit < 1:
            raise ValueError("limit must be greater than zero")
        candidate_limit = max(limit * self.settings.retrieval_candidate_multiplier, limit)
        active_filters = (filters or SearchFilters()).model_dump()
        vector_results = self.store.vector_search(
            document_set_id,
            self.provider.embed([query])[0],
            candidate_limit,
            **active_filters,
        )
        lexical_results = self.store.lexical_search(
            document_set_id,
            query,
            candidate_limit,
            **active_filters,
        )
        merged = self._merge(vector_results, lexical_results)
        return [SearchResult.model_validate(item) for item in merged[:limit]]

    @staticmethod
    def _merge(
        vector_results: list[dict[str, Any]], lexical_results: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        merged: dict[int, dict[str, Any]] = {}
        for rank, row in enumerate(vector_results, start=1):
            item = merged.setdefault(row["id"], dict(row))
            item["vector_rank"] = rank
            item["fusion_score"] = item.get("fusion_score", 0.0) + 1 / (60 + rank)
        for rank, row in enumerate(lexical_results, start=1):
            item = merged.setdefault(row["id"], dict(row))
            item["lexical_rank"] = rank
            item["lexical_score"] = row.get("lexical_score")
            item["fusion_score"] = item.get("fusion_score", 0.0) + 1 / (60 + rank)
        return sorted(merged.values(), key=lambda item: (-item["fusion_score"], item["id"]))
