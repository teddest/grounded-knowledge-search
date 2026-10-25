from __future__ import annotations

from uuid import uuid4

import pytest

from grounded_knowledge_api.config import Settings
from grounded_knowledge_api.retrieval import HybridRetriever, SearchFilters, SearchResult


class Provider:
    model = "test-embedding"

    def embed(self, texts):
        return [[0.1, 0.2] for _ in texts]


class Store:
    def __init__(self, vectors, lexical):
        self.vectors = vectors
        self.lexical = lexical
        self.vector_call = None
        self.lexical_call = None

    def get_document_set(self, _id):
        return {"id": _id}

    def vector_search(self, document_set_id, embedding, limit, **filters):
        self.vector_call = (document_set_id, embedding, limit, filters)
        return self.vectors

    def lexical_search(self, document_set_id, query, limit, **filters):
        self.lexical_call = (document_set_id, query, limit, filters)
        return self.lexical


def row(identifier: int, content: str = "content"):
    return {
        "id": identifier,
        "source_path": f"docs/{identifier}.md",
        "title": "Policy",
        "category": "billing",
        "status": "current",
        "version": "2025.1",
        "effective_date": None,
        "heading_path": ["Policy"],
        "start_line": 1,
        "end_line": 2,
        "content": content,
        "similarity": 0.9,
    }


def test_hybrid_search_merges_and_ranks_both_result_sets():
    document_set_id = uuid4()
    store = Store(
        [row(1), row(2)], [{**row(2), "lexical_score": 2.0}, {**row(3), "lexical_score": 1.0}]
    )
    retriever = HybridRetriever(
        store,
        Provider(),
        Settings(retrieval_candidate_multiplier=3, embedding_dimensions=2),
    )

    results = retriever.search(
        document_set_id,
        "refund",
        SearchFilters(category="billing", status="current"),
        limit=2,
    )

    assert [result.id for result in results] == [2, 1]
    assert results[0].vector_rank == 2
    assert results[0].lexical_rank == 1
    assert store.vector_call[2] == 6
    assert store.vector_call[3] == {"category": "billing", "status": "current", "version": None}
    assert store.lexical_call[1] == "refund"


def test_hybrid_search_handles_empty_candidate_lists_and_limit():
    store = Store([], [])
    retriever = HybridRetriever(store, Provider(), Settings(embedding_dimensions=2))

    assert retriever.search(uuid4(), "nothing") == []


def test_hybrid_search_validates_query_and_limit():
    retriever = HybridRetriever(Store([], []), Provider(), Settings(embedding_dimensions=2))

    with pytest.raises(ValueError, match="must not be empty"):
        retriever.search(uuid4(), "   ")
    with pytest.raises(ValueError, match="greater than zero"):
        retriever.search(uuid4(), "query", limit=0)


def test_merge_deduplicates_and_uses_id_for_ties():
    merged = HybridRetriever._merge(
        [{**row(2), "similarity": 0.5}],
        [{**row(1), "lexical_score": 0.5}],
    )

    assert [item["id"] for item in merged] == [1, 2]
    assert merged[0].get("vector_rank") is None
    assert merged[1].get("lexical_rank") is None


def test_search_result_is_typed():
    result = SearchResult.model_validate({**row(1), "fusion_score": 0.1})

    assert result.source_path == "docs/1.md"
