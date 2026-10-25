from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Any, Protocol

from openai import OpenAI

from .config import Settings


class EmbeddingProviderError(RuntimeError):
    """Raised when an embedding request cannot be completed safely."""


class EmbeddingProvider(Protocol):
    model: str

    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


class OpenRouterEmbeddingProvider:
    def __init__(
        self,
        settings: Settings,
        client: Any | None = None,
        sleep: Any = time.sleep,
    ) -> None:
        self.model = settings.openrouter_embedding_model
        self.dimensions = settings.embedding_dimensions
        self.max_attempts = 3
        self.retry_delay_seconds = 0.25
        self._settings = settings
        self._client = client
        self._sleep = sleep

    def _client_or_create(self) -> Any:
        if self._client is not None:
            return self._client
        if not self._settings.openrouter_api_key:
            raise EmbeddingProviderError("OPENROUTER_API_KEY is not configured")
        self._client = OpenAI(
            api_key=self._settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": self._settings.openrouter_site_url,
                "X-Title": self._settings.openrouter_app_name,
            },
            timeout=30.0,
            max_retries=0,
        )
        return self._client

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        client = self._client_or_create()
        last_error: Exception | None = None
        for attempt in range(self.max_attempts):
            try:
                response = client.embeddings.create(
                    model=self.model,
                    input=list(texts),
                    dimensions=self.dimensions,
                )
                vectors = [
                    item.embedding for item in sorted(response.data, key=lambda item: item.index)
                ]
                if len(vectors) != len(texts):
                    raise EmbeddingProviderError(
                        f"provider returned {len(vectors)} vectors for {len(texts)} inputs"
                    )
                wrong_dimensions = [
                    len(vector) for vector in vectors if len(vector) != self.dimensions
                ]
                if wrong_dimensions:
                    raise EmbeddingProviderError(
                        f"provider returned vector dimensions {wrong_dimensions}; "
                        f"expected {self.dimensions}"
                    )
                return vectors
            except EmbeddingProviderError:
                raise
            except Exception as exc:
                last_error = exc
                if attempt + 1 < self.max_attempts:
                    self._sleep(self.retry_delay_seconds)
        raise EmbeddingProviderError("OpenRouter embedding request failed") from last_error
