from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Any, Protocol, cast

from openai import OpenAI

from .config import Settings


class ChatProviderError(RuntimeError):
    """Raised when a grounded answer cannot be generated safely."""


class ChatProvider(Protocol):
    model: str

    def complete(self, messages: Sequence[dict[str, str]]) -> str: ...


class OpenRouterChatProvider:
    def __init__(
        self,
        settings: Settings,
        client: Any | None = None,
        sleep: Any = time.sleep,
    ) -> None:
        self.model = settings.openrouter_chat_model
        self.max_tokens = settings.answer_max_tokens
        self._settings = settings
        self._client = client
        self._sleep = sleep

    def _client_or_create(self) -> Any:
        if self._client is not None:
            return self._client
        if not self._settings.openrouter_api_key:
            raise ChatProviderError("OPENROUTER_API_KEY is not configured")
        self._client = OpenAI(
            api_key=self._settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": self._settings.openrouter_site_url,
                "X-Title": self._settings.openrouter_app_name,
            },
            timeout=60.0,
            max_retries=0,
        )
        return self._client

    def complete(self, messages: Sequence[dict[str, str]]) -> str:
        if not messages:
            raise ChatProviderError("chat messages must not be empty")
        client = self._client_or_create()
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=list(messages),
                    temperature=0.1,
                    max_tokens=self.max_tokens,
                )
                content = cast(str | None, response.choices[0].message.content)
                if not content or not content.strip():
                    raise ChatProviderError("chat provider returned an empty answer")
                return content.strip()
            except ChatProviderError:
                raise
            except Exception as exc:
                last_error = exc
                if attempt < 2:
                    self._sleep(0.25)
        raise ChatProviderError("OpenRouter chat request failed") from last_error
