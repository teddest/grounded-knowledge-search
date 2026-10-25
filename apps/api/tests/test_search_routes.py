from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from grounded_knowledge_api.config import Settings, get_settings
from grounded_knowledge_api.embeddings import EmbeddingProviderError
from grounded_knowledge_api.main import create_app
from grounded_knowledge_api.routes import ingestion as ingestion_routes
from grounded_knowledge_api.routes import search as search_routes


class Provider:
    model = "test-embedding"

    def embed(self, texts):
        return [[0.1, 0.2] for _ in texts]


class Store:
    def __init__(self, document_set=None):
        self.document_set = document_set

    def get_document_set(self, _document_set_id):
        return self.document_set

    def vector_search(self, *_args, **_kwargs):
        return [
            {
                "id": 1,
                "source_path": "policies/refunds.md",
                "title": "Refund Policy",
                "category": "billing",
                "status": "current",
                "version": "2025.1",
                "heading_path": ["Refunds"],
                "start_line": 1,
                "end_line": 3,
                "content": "Annual refunds are available.",
                "similarity": 0.9,
            }
        ]

    def lexical_search(self, *_args, **_kwargs):
        return [
            {
                "id": 1,
                "source_path": "policies/refunds.md",
                "title": "Refund Policy",
                "category": "billing",
                "status": "current",
                "version": "2025.1",
                "heading_path": ["Refunds"],
                "start_line": 1,
                "end_line": 3,
                "content": "Annual refunds are available.",
                "lexical_score": 1.0,
            }
        ]


def client_for(tmp_path: Path, store: Store, provider=None):
    settings = Settings(repository_root=str(tmp_path), api_cors_origins=[], embedding_dimensions=2)
    provider = provider or Provider()
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[ingestion_routes.get_store] = lambda: store
    app.dependency_overrides[search_routes.get_embedding_provider] = lambda: provider
    return TestClient(app)


def test_search_returns_hybrid_result(tmp_path):
    document_set = {"id": uuid4()}
    with client_for(tmp_path, Store(document_set)) as client:
        response = client.post(
            "/api/v1/search",
            json={
                "document_set_id": str(document_set["id"]),
                "query": "annual refund",
                "limit": 5,
                "filters": {"category": "billing"},
            },
        )

    assert response.status_code == 200
    assert response.json()["results"][0]["source_path"] == "policies/refunds.md"
    assert response.json()["results"][0]["vector_rank"] == 1


def test_search_handles_not_found_and_validation(tmp_path):
    with client_for(tmp_path, Store()) as client:
        not_found = client.post(
            "/api/v1/search", json={"document_set_id": str(uuid4()), "query": "refund"}
        )
        invalid = client.post("/api/v1/search", json={"document_set_id": str(uuid4()), "query": ""})

    assert not_found.status_code == 404
    assert invalid.status_code == 422


def test_search_maps_provider_value_and_internal_errors(monkeypatch, tmp_path):
    document_set = {"id": uuid4()}

    class ProviderFailure:
        model = "test"

        def embed(self, _texts):
            raise EmbeddingProviderError("provider unavailable")

    with client_for(tmp_path, Store(document_set), ProviderFailure()) as client:
        provider_response = client.post(
            "/api/v1/search", json={"document_set_id": str(document_set["id"]), "query": "refund"}
        )
    assert provider_response.status_code == 503

    monkeypatch.setattr(
        search_routes.HybridRetriever,
        "search",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("failure")),
    )
    with client_for(tmp_path, Store(document_set)) as client:
        error_response = client.post(
            "/api/v1/search", json={"document_set_id": str(document_set["id"]), "query": "refund"}
        )
    assert error_response.status_code == 500


def test_search_maps_empty_query_value_error(monkeypatch, tmp_path):
    document_set = {"id": uuid4()}
    monkeypatch.setattr(
        search_routes.HybridRetriever,
        "search",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("query must not be empty")),
    )
    with client_for(tmp_path, Store(document_set)) as client:
        response = client.post(
            "/api/v1/search", json={"document_set_id": str(document_set["id"]), "query": "refund"}
        )
    assert response.status_code == 400
