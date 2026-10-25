from __future__ import annotations

from uuid import uuid4

import pytest

from grounded_knowledge_api.config import Settings
from grounded_knowledge_api.indexing import (
    EmbeddingIndexingService,
    _batches,
    embedding_input,
    input_hash,
)


class FakeProvider:
    model = "test-embedding"

    def __init__(self, vectors=None):
        self.vectors = vectors
        self.inputs: list[list[str]] = []

    def embed(self, texts):
        self.inputs.append(list(texts))
        if self.vectors is not None:
            return self.vectors
        return [[0.1, 0.2] for _ in texts]


class FakeStore:
    def __init__(self, sections):
        self.sections = sections
        self.updates = []

    def pending_embedding_sections(self, document_set_id, embedding_model):
        return self.sections

    def update_section_embeddings(self, embeddings):
        self.updates.extend(embeddings)


def section(section_id: int, content: str):
    return {
        "id": section_id,
        "title": "Refund Policy",
        "category": "billing",
        "status": "current",
        "version": "2025.1",
        "heading_path": ["Refunds"],
        "source_path": "policies/refunds.md",
        "content": content,
    }


def test_embedding_input_contains_context_and_hash_is_stable():
    text = embedding_input(section(1, "Annual refunds are allowed."))

    assert "Title: Refund Policy" in text
    assert "Heading: Refunds" in text
    assert "Annual refunds" in text
    assert input_hash(text) == input_hash(text)


def test_batches_split_items_and_reject_invalid_size():
    items = [{"id": index} for index in range(5)]
    assert [len(batch) for batch in _batches(items, 2)] == [2, 2, 1]
    assert _batches([], 2) == []
    with pytest.raises(ValueError, match="greater than zero"):
        _batches(items, 0)


def test_indexing_batches_and_persists_embeddings():
    sections = [section(1, "one"), section(2, "two"), section(3, "three")]
    store = FakeStore(sections)
    provider = FakeProvider()
    settings = Settings(embedding_batch_size=2, embedding_dimensions=2)

    result = EmbeddingIndexingService(store, provider, settings).index_document_set(uuid4())

    assert result == (3, 3)
    assert [len(batch) for batch in provider.inputs] == [2, 1]
    assert [update[0] for update in store.updates] == [1, 2, 3]
    assert all(update[2] == "test-embedding" for update in store.updates)


def test_indexing_rejects_wrong_vector_count():
    store = FakeStore([section(1, "one"), section(2, "two")])
    provider = FakeProvider(vectors=[[0.1, 0.2]])

    with pytest.raises(ValueError, match="wrong number"):
        EmbeddingIndexingService(
            store, provider, Settings(embedding_batch_size=2, embedding_dimensions=2)
        ).index_document_set(uuid4())


def test_indexing_with_no_pending_sections_is_a_noop():
    store = FakeStore([])
    provider = FakeProvider()

    assert EmbeddingIndexingService(
        store, provider, Settings(embedding_batch_size=2, embedding_dimensions=2)
    ).index_document_set(uuid4()) == (0, 0)
    assert provider.inputs == []
