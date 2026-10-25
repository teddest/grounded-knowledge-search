from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from grounded_knowledge_api.chat import ChatProviderError, OpenRouterChatProvider
from grounded_knowledge_api.config import Settings


def provider_for(client=None, sleep=None):
    return OpenRouterChatProvider(
        Settings(openrouter_api_key="key", answer_max_tokens=300),
        client=client,
        sleep=sleep or (lambda _seconds: None),
    )


def response(content):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


def test_chat_rejects_empty_messages():
    with pytest.raises(ChatProviderError, match="must not be empty"):
        provider_for().complete([])


def test_chat_returns_trimmed_content_and_uses_settings():
    client = Mock()
    client.chat.completions.create.return_value = response("  Answer [1]  ")

    result = provider_for(client).complete([{"role": "user", "content": "Question"}])

    assert result == "Answer [1]"
    client.chat.completions.create.assert_called_once()
    assert client.chat.completions.create.call_args.kwargs["max_tokens"] == 300


def test_chat_requires_key_without_injected_client():
    provider = OpenRouterChatProvider(Settings(openrouter_api_key=""))

    with pytest.raises(ChatProviderError, match="OPENROUTER_API_KEY"):
        provider.complete([{"role": "user", "content": "Question"}])


def test_chat_creates_openrouter_client(monkeypatch):
    client = Mock()
    client.chat.completions.create.return_value = response("answer")
    constructor = Mock(return_value=client)
    monkeypatch.setattr("grounded_knowledge_api.chat.OpenAI", constructor)

    assert provider_for().complete([{"role": "user", "content": "Question"}]) == "answer"
    assert constructor.call_args.kwargs["base_url"] == "https://openrouter.ai/api/v1"


def test_chat_retries_transient_failure():
    client = Mock()
    client.chat.completions.create.side_effect = [RuntimeError("temporary"), response("answer")]
    sleeps: list[float] = []

    assert (
        provider_for(client, sleeps.append).complete([{"role": "user", "content": "Question"}])
        == "answer"
    )
    assert sleeps == [0.25]


def test_chat_rejects_empty_response_without_retry():
    client = Mock()
    client.chat.completions.create.return_value = response("  ")

    with pytest.raises(ChatProviderError, match="empty answer"):
        provider_for(client).complete([{"role": "user", "content": "Question"}])
    assert client.chat.completions.create.call_count == 1


def test_chat_reports_exhausted_retries():
    client = Mock()
    client.chat.completions.create.side_effect = RuntimeError("down")

    with pytest.raises(ChatProviderError, match="request failed"):
        provider_for(client).complete([{"role": "user", "content": "Question"}])
    assert client.chat.completions.create.call_count == 3
