from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from grounded_knowledge_api.chat import ChatProviderError
from grounded_knowledge_api.config import Settings, get_settings
from grounded_knowledge_api.main import create_app
from grounded_knowledge_api.routes import answers as answer_routes
from grounded_knowledge_api.routes import ingestion as ingestion_routes


class Store:
    def __init__(self, document_set=None):
        self.document_set = document_set

    def get_document_set(self, _id):
        return self.document_set

    def vector_search(self, *_args, **_kwargs):
        return [self.row()]

    def lexical_search(self, *_args, **_kwargs):
        return [self.row()]

    @staticmethod
    def row():
        return {
            "id": 1,
            "source_path": "policies/refunds.md",
            "title": "Refund Policy",
            "category": "billing",
            "status": "current",
            "version": "2025.1",
            "heading_path": ["Refunds"],
            "start_line": 1,
            "end_line": 4,
            "content": "Annual refunds are available.",
            "similarity": 0.9,
            "lexical_score": 1.0,
        }


class Embeddings:
    model = "test-embedding"

    def embed(self, texts):
        return [[0.1, 0.2] for _ in texts]


class Chat:
    def __init__(self, error=None):
        self.error = error

    def complete(self, messages):
        if self.error:
            raise self.error
        return "The answer is supported [1]."


def client_for(tmp_path: Path, store: Store, embedding=None, chat=None):
    settings = Settings(repository_root=str(tmp_path), api_cors_origins=[], embedding_dimensions=2)
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[ingestion_routes.get_store] = lambda: store
    app.dependency_overrides[answer_routes.get_embedding_provider] = lambda: (
        embedding or Embeddings()
    )
    app.dependency_overrides[answer_routes.get_chat_provider] = lambda: chat or Chat()
    return TestClient(app)


def test_ask_returns_answer_and_sources(tmp_path):
    document_set = {"id": uuid4()}
    with client_for(tmp_path, Store(document_set)) as client:
        response = client.post(
            "/api/v1/ask",
            json={
                "document_set_id": str(document_set["id"]),
                "question": "What is the refund rule?",
            },
        )

    assert response.status_code == 200
    assert response.json()["answer"] == "The answer is supported [1]."
    assert response.json()["sources"][0]["source_path"] == "policies/refunds.md"


def test_ask_handles_not_found_and_validation(tmp_path):
    with client_for(tmp_path, Store()) as client:
        not_found = client.post(
            "/api/v1/ask", json={"document_set_id": str(uuid4()), "question": "refund"}
        )
        invalid = client.post("/api/v1/ask", json={"document_set_id": str(uuid4()), "question": ""})

    assert not_found.status_code == 404
    assert invalid.status_code == 422


def test_ask_maps_provider_errors(tmp_path):
    document_set = {"id": uuid4()}

    class FailingEmbeddings:
        model = "test"

        def embed(self, _texts):
            from grounded_knowledge_api.embeddings import EmbeddingProviderError

            raise EmbeddingProviderError("embedding unavailable")

    with client_for(tmp_path, Store(document_set), embedding=FailingEmbeddings()) as client:
        embedding_response = client.post(
            "/api/v1/ask", json={"document_set_id": str(document_set["id"]), "question": "refund"}
        )
    assert embedding_response.status_code == 503

    with client_for(
        tmp_path, Store(document_set), chat=Chat(ChatProviderError("chat down"))
    ) as client:
        chat_response = client.post(
            "/api/v1/ask", json={"document_set_id": str(document_set["id"]), "question": "refund"}
        )
    assert chat_response.status_code == 503


def test_ask_maps_value_and_internal_errors(monkeypatch, tmp_path):
    document_set = {"id": uuid4()}
    monkeypatch.setattr(
        answer_routes.GroundedAnswerService,
        "answer",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("bad question")),
    )
    with client_for(tmp_path, Store(document_set)) as client:
        value_response = client.post(
            "/api/v1/ask", json={"document_set_id": str(document_set["id"]), "question": "refund"}
        )
    assert value_response.status_code == 400

    monkeypatch.setattr(
        answer_routes.GroundedAnswerService,
        "answer",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("failure")),
    )
    with client_for(tmp_path, Store(document_set)) as client:
        internal_response = client.post(
            "/api/v1/ask", json={"document_set_id": str(document_set["id"]), "question": "refund"}
        )
    assert internal_response.status_code == 500


def test_chat_provider_dependency_uses_settings():
    provider = answer_routes.get_chat_provider(Settings(openrouter_api_key="key"))
    assert provider.model == "openai/gpt-4o-mini"
