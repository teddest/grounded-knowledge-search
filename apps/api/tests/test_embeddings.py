from __future__ import annotations

from unittest.mock import Mock

import pytest

from grounded_knowledge_api.config import Settings
from grounded_knowledge_api.embeddings import EmbeddingProviderError, OpenRouterEmbeddingProvider


class Item:
    def __init__(self, index: int, embedding: list[float]):
        self.index = index
        self.embedding = embedding


class Response:
    def __init__(self, data):
        self.data = data


def provider_for(client, dimensions=2, sleep=None):
    return OpenRouterEmbeddingProvider(
        Settings(
            openrouter_api_key="key",
            embedding_dimensions=dimensions,
            openrouter_embedding_model="test-embedding",
        ),
        client=client,
        sleep=sleep or (lambda _seconds: None),
    )


def test_empty_input_does_not_call_provider():
    client = Mock()

    assert provider_for(client).embed([]) == []
    client.embeddings.create.assert_not_called()


def test_embed_sorts_results_and_passes_configuration():
    client = Mock()
    client.embeddings.create.return_value = Response([Item(1, [0.2, 0.3]), Item(0, [0.1, 0.2])])

    result = provider_for(client).embed(["first", "second"])

    assert result == [[0.1, 0.2], [0.2, 0.3]]
    client.embeddings.create.assert_called_once_with(
        model="test-embedding", input=["first", "second"], dimensions=2
    )


def test_provider_requires_key_when_no_client_is_injected():
    provider = OpenRouterEmbeddingProvider(Settings(embedding_dimensions=2, openrouter_api_key=""))

    with pytest.raises(EmbeddingProviderError, match="OPENROUTER_API_KEY"):
        provider.embed(["text"])


def test_provider_creates_openrouter_client(monkeypatch):
    client = Mock()
    client.embeddings.create.return_value = Response([Item(0, [0.1, 0.2])])
    constructor = Mock(return_value=client)
    monkeypatch.setattr("grounded_knowledge_api.embeddings.OpenAI", constructor)
    settings = Settings(
        openrouter_api_key="key",
        embedding_dimensions=2,
        openrouter_site_url="http://example",
        openrouter_app_name="app",
    )

    assert OpenRouterEmbeddingProvider(settings).embed(["text"]) == [[0.1, 0.2]]
    constructor.assert_called_once()
    assert constructor.call_args.kwargs["base_url"] == "https://openrouter.ai/api/v1"


def test_provider_retries_transient_errors():
    client = Mock()
    client.embeddings.create.side_effect = [
        RuntimeError("temporary"),
        Response([Item(0, [0.1, 0.2])]),
    ]
    sleeps: list[float] = []

    result = provider_for(client, sleep=sleeps.append).embed(["text"])

    assert result == [[0.1, 0.2]]
    assert sleeps == [0.25]


def test_provider_reports_exhausted_retries():
    client = Mock()
    client.embeddings.create.side_effect = RuntimeError("provider down")

    with pytest.raises(EmbeddingProviderError, match="request failed"):
        provider_for(client).embed(["text"])

    assert client.embeddings.create.call_count == 3


def test_provider_rejects_wrong_result_count():
    client = Mock()
    client.embeddings.create.return_value = Response([Item(0, [0.1, 0.2])])

    with pytest.raises(EmbeddingProviderError, match="returned 1 vectors"):
        provider_for(client).embed(["one", "two"])


def test_provider_rejects_wrong_dimensions():
    client = Mock()
    client.embeddings.create.return_value = Response([Item(0, [0.1, 0.2, 0.3])])

    with pytest.raises(EmbeddingProviderError, match="dimensions"):
        provider_for(client).embed(["text"])


def test_provider_does_not_retry_provider_validation_errors():
    client = Mock()
    client.embeddings.create.return_value = Response([Item(0, [0.1, 0.2, 0.3])])

    with pytest.raises(EmbeddingProviderError):
        provider_for(client).embed(["text"])

    assert client.embeddings.create.call_count == 1
