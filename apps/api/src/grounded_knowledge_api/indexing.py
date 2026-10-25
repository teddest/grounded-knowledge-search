from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any, Protocol
from uuid import UUID

from .config import Settings
from .embeddings import EmbeddingProvider


class EmbeddingStore(Protocol):
    def pending_embedding_sections(
        self, document_set_id: UUID, embedding_model: str
    ) -> list[dict[str, Any]]: ...

    def update_section_embeddings(
        self,
        embeddings: list[tuple[int, list[float], str, str]],
    ) -> None: ...


def embedding_input(section: dict[str, Any]) -> str:
    heading_path = " > ".join(section.get("heading_path") or [])
    metadata = [
        f"Title: {section.get('title') or ''}",
        f"Category: {section.get('category') or ''}",
        f"Status: {section.get('status') or ''}",
        f"Version: {section.get('version') or ''}",
        f"Heading: {heading_path}",
        f"Source: {section.get('source_path') or ''}",
    ]
    return "\n".join(metadata) + f"\n\n{section['content']}"


def input_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class EmbeddingIndexingService:
    def __init__(
        self,
        store: EmbeddingStore,
        provider: EmbeddingProvider,
        settings: Settings,
    ) -> None:
        self.store = store
        self.provider = provider
        self.settings = settings

    def index_document_set(self, document_set_id: UUID) -> tuple[int, int]:
        sections = self.store.pending_embedding_sections(document_set_id, self.provider.model)
        updated = 0
        for batch in _batches(sections, self.settings.embedding_batch_size):
            texts = [embedding_input(section) for section in batch]
            vectors = self.provider.embed(texts)
            if len(vectors) != len(batch):
                raise ValueError("embedding provider returned the wrong number of vectors")
            updates = [
                (int(section["id"]), vector, self.provider.model, input_hash(text))
                for section, text, vector in zip(batch, texts, vectors, strict=True)
            ]
            self.store.update_section_embeddings(updates)
            updated += len(updates)
        return len(sections), updated


def _batches(items: Sequence[dict[str, Any]], size: int) -> list[Sequence[dict[str, Any]]]:
    if size < 1:
        raise ValueError("embedding batch size must be greater than zero")
    return [items[start : start + size] for start in range(0, len(items), size)]
