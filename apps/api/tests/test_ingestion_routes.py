from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from grounded_knowledge_api.config import Settings, get_settings
from grounded_knowledge_api.database import DatabaseDocumentStore
from grounded_knowledge_api.embeddings import EmbeddingProviderError
from grounded_knowledge_api.ingestion import IngestionError
from grounded_knowledge_api.main import create_app
from grounded_knowledge_api.routes import ingestion as ingestion_routes
from grounded_knowledge_api.routes.ingestion import get_store, resolve_document_root


class FakeStore:
    def __init__(self, document_set=None):
        self.document_set = document_set
        self.document_sets = [document_set] if document_set else []
        self.created = []

    def create_document_set(self, name, root_path):
        row = {"id": uuid4(), "name": name, "root_path": root_path, "status": "registered"}
        self.created.append(row)
        self.document_set = row
        self.document_sets.append(row)
        return row

    def list_document_sets(self):
        return self.document_sets

    def get_document_set(self, document_set_id):
        return next((row for row in self.document_sets if row["id"] == document_set_id), None)


def client_for(tmp_path, store):
    settings = Settings(repository_root=str(tmp_path), api_cors_origins=[])
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_store] = lambda: store
    app.dependency_overrides[ingestion_routes.get_embedding_provider] = lambda: object()
    return TestClient(app)


def test_resolve_document_root_rejects_escape_and_invalid_paths(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    assert resolve_document_root(str(tmp_path), "docs") == docs.resolve()

    with pytest.raises(IngestionError, match="inside"):
        resolve_document_root(str(tmp_path), "../outside")
    with pytest.raises(IngestionError, match="not a directory"):
        resolve_document_root(str(tmp_path), "missing")
    file_path = tmp_path / "file.txt"
    file_path.write_text("file", encoding="utf-8")
    with pytest.raises(IngestionError, match="not a directory"):
        resolve_document_root(str(tmp_path), "file.txt")


def test_discover_document_sets_is_idempotent_and_preserves_custom(tmp_path):
    documents = tmp_path / "documents"
    (documents / "policies").mkdir(parents=True)
    (documents / "procedures").mkdir()
    (documents / "policies" / "refunds.md").write_text("# Refunds\n\nRule", encoding="utf-8")
    custom = {"id": uuid4(), "name": "Custom", "root_path": "custom", "status": "registered"}
    store = FakeStore(custom)
    settings = Settings(
        repository_root=str(tmp_path), document_root="documents", api_cors_origins=[]
    )
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_store] = lambda: store

    with TestClient(app) as client:
        first = client.post("/api/v1/document-sets/discover")
        second = client.post("/api/v1/document-sets/discover")

    assert first.status_code == 200
    assert [item["root_path"] for item in first.json()] == [
        "documents",
        "documents/policies",
        "custom",
    ]
    assert len(store.created) == 2
    assert second.json() == first.json()


def test_discover_document_sets_rejects_missing_corpus(tmp_path):
    settings = Settings(
        repository_root=str(tmp_path), document_root="documents", api_cors_origins=[]
    )
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_store] = lambda: FakeStore()

    with TestClient(app) as client:
        response = client.post("/api/v1/document-sets/discover")

    assert response.status_code == 400


def test_create_and_list_document_sets(tmp_path):
    (tmp_path / "docs").mkdir()
    store = FakeStore()
    with client_for(tmp_path, store) as client:
        response = client.post("/api/v1/document-sets", json={"name": "Docs", "path": "docs"})
        assert response.status_code == 201
        assert response.json()["root_path"] == "docs"
        listed = client.get("/api/v1/document-sets")

    assert listed.status_code == 200
    assert listed.json()[0]["name"] == "Docs"


def test_create_document_set_rejects_path_escape(tmp_path):
    with client_for(tmp_path, FakeStore()) as client:
        response = client.post(
            "/api/v1/document-sets", json={"name": "Invalid", "path": "../outside"}
        )
    assert response.status_code == 400
    assert "inside" in response.json()["detail"]


def test_ingest_document_set_success(monkeypatch, tmp_path):
    (tmp_path / "docs").mkdir()
    document_set = {"id": uuid4(), "name": "Docs", "root_path": "docs", "status": "registered"}
    store = FakeStore(document_set)
    monkeypatch.setattr(ingestion_routes, "ingest_document_set", lambda *_args: (3, 7))

    with client_for(tmp_path, store) as client:
        response = client.post(f"/api/v1/document-sets/{document_set['id']}/ingest")

    assert response.status_code == 200
    assert response.json()["documents_seen"] == 3
    assert response.json()["sections_seen"] == 7


def test_ingest_document_set_not_found():
    store = FakeStore()
    with client_for(Path("/tmp"), store) as client:
        response = client.post(f"/api/v1/document-sets/{uuid4()}/ingest")
    assert response.status_code == 404


def test_ingest_document_set_maps_errors(monkeypatch, tmp_path):
    (tmp_path / "docs").mkdir()
    document_set = {"id": uuid4(), "name": "Docs", "root_path": "docs", "status": "registered"}
    store = FakeStore(document_set)

    monkeypatch.setattr(
        ingestion_routes,
        "ingest_document_set",
        lambda *_args: (_ for _ in ()).throw(IngestionError("bad document")),
    )
    with client_for(tmp_path, store) as client:
        bad_response = client.post(f"/api/v1/document-sets/{document_set['id']}/ingest")
    assert bad_response.status_code == 400
    assert bad_response.json()["detail"] == "bad document"

    monkeypatch.setattr(
        ingestion_routes,
        "ingest_document_set",
        lambda *_args: (_ for _ in ()).throw(RuntimeError("database down")),
    )
    with client_for(tmp_path, store) as client:
        error_response = client.post(f"/api/v1/document-sets/{document_set['id']}/ingest")
    assert error_response.status_code == 500
    assert error_response.json()["detail"] == "document ingestion failed"


def test_index_embeddings_success(monkeypatch, tmp_path):
    (tmp_path / "docs").mkdir()
    document_set = {"id": uuid4(), "name": "Docs", "root_path": "docs", "status": "ready"}
    store = FakeStore(document_set)

    class SuccessService:
        def __init__(self, *_args):
            pass

        def index_document_set(self, _document_set_id):
            return 4, 4

    monkeypatch.setattr(ingestion_routes, "EmbeddingIndexingService", SuccessService)
    with client_for(tmp_path, store) as client:
        response = client.post(f"/api/v1/document-sets/{document_set['id']}/index")

    assert response.status_code == 200
    assert response.json()["sections_embedded"] == 4


def test_index_embeddings_maps_provider_and_internal_errors(monkeypatch, tmp_path):
    (tmp_path / "docs").mkdir()
    document_set = {"id": uuid4(), "name": "Docs", "root_path": "docs", "status": "ready"}
    store = FakeStore(document_set)

    class ProviderErrorService:
        def __init__(self, *_args):
            pass

        def index_document_set(self, _document_set_id):
            raise EmbeddingProviderError("provider unavailable")

    monkeypatch.setattr(ingestion_routes, "EmbeddingIndexingService", ProviderErrorService)
    with client_for(tmp_path, store) as client:
        provider_response = client.post(f"/api/v1/document-sets/{document_set['id']}/index")
    assert provider_response.status_code == 503

    class InternalErrorService:
        def __init__(self, *_args):
            pass

        def index_document_set(self, _document_set_id):
            raise RuntimeError("database unavailable")

    monkeypatch.setattr(ingestion_routes, "EmbeddingIndexingService", InternalErrorService)
    with client_for(tmp_path, store) as client:
        internal_response = client.post(f"/api/v1/document-sets/{document_set['id']}/index")
    assert internal_response.status_code == 500


def test_index_embeddings_not_found(tmp_path):
    with client_for(tmp_path, FakeStore()) as client:
        response = client.post(f"/api/v1/document-sets/{uuid4()}/index")
    assert response.status_code == 404


def test_embedding_provider_dependency_uses_settings():
    provider = ingestion_routes.get_embedding_provider(
        Settings(openrouter_api_key="key", embedding_dimensions=2)
    )
    assert provider.model == "openai/text-embedding-3-small"


def test_store_dependency_type_is_document_store():
    settings = Settings(database_url="postgresql://example")
    store = get_store(settings)
    assert isinstance(store, DatabaseDocumentStore)
