from __future__ import annotations

from uuid import uuid4

import pytest

from grounded_knowledge_api.answering import (
    GroundedAnswerService,
    answer_messages,
    format_context,
)
from grounded_knowledge_api.config import Settings
from grounded_knowledge_api.retrieval import SearchFilters, SearchResult


def result(identifier: int, content: str = "Evidence content") -> SearchResult:
    return SearchResult(
        id=identifier,
        source_path=f"docs/{identifier}.md",
        title="Policy",
        status="current",
        version="2025.1",
        heading_path=["Rules"],
        start_line=2,
        end_line=4,
        content=content,
        fusion_score=0.1,
    )


class Retriever:
    def __init__(self, results):
        self.results = results
        self.calls = []

    def search(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return self.results


class Chat:
    def __init__(self, answer="Grounded answer [1]"):
        self.answer_text = answer
        self.messages = []

    def complete(self, messages):
        self.messages.append(messages)
        return self.answer_text


def test_format_context_preserves_citations_and_truncates():
    context, sources = format_context([result(1, "a" * 100), result(2, "b")], 130)

    assert "[1]" in context
    assert "[truncated]" in context
    assert [source.id for source in sources] == [1]


def test_format_context_rejects_invalid_limit_and_handles_empty_results():
    with pytest.raises(ValueError, match="greater than zero"):
        format_context([result(1)], 0)
    assert format_context([], 100) == ("", [])


def test_answer_messages_include_grounding_instructions():
    messages = answer_messages("Question", "[1] evidence")

    assert messages[0]["role"] == "system"
    assert "Do not invent" in messages[0]["content"]
    assert "[1] evidence" in messages[1]["content"]


def test_service_returns_explicit_no_evidence_without_calling_chat():
    retriever = Retriever([])
    chat = Chat()
    service = GroundedAnswerService(retriever, chat, Settings())

    answer = service.answer(uuid4(), "unsupported", SearchFilters(), 5)

    assert answer.sources == []
    assert "could not find" in answer.answer
    assert chat.messages == []


def test_service_generates_grounded_answer_and_sources():
    retriever = Retriever([result(1), result(2)])
    chat = Chat()
    settings = Settings(answer_max_context_characters=1000)

    answer = GroundedAnswerService(retriever, chat, settings).answer(
        uuid4(), "What is the rule?", SearchFilters(status="current"), 2
    )

    assert answer.answer == "Grounded answer [1]"
    assert [source.id for source in answer.sources] == [1, 2]
    assert chat.messages[0][1]["content"].startswith("Question:")
    assert retriever.calls[0][0][3] == 2
