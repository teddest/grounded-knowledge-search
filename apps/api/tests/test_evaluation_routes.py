from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from grounded_knowledge_api.config import Settings, get_settings
from grounded_knowledge_api.embeddings import EmbeddingProviderError
from grounded_knowledge_api.evaluation import EvaluationMetrics, EvaluationReport
from grounded_knowledge_api.main import create_app
from grounded_knowledge_api.routes import evaluation as evaluation_routes
from grounded_knowledge_api.routes import ingestion as ingestion_routes


class Store:
    def __init__(self, document_set=None):
        self.document_set = document_set

    def get_document_set(self, _id):
        return self.document_set


def client_for(tmp_path: Path, store: Store, provider=None):
    settings = Settings(repository_root=str(tmp_path), api_cors_origins=[])
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[ingestion_routes.get_store] = lambda: store
    app.dependency_overrides[evaluation_routes.get_embedding_provider] = lambda: (
        provider or object()
    )
    return TestClient(app)


def report():
    return EvaluationReport(
        k=5,
        query_count=1,
        metrics=EvaluationMetrics(hit_at_k=1.0, precision_at_k=0.2, recall_at_k=1.0, mrr=1.0),
        cases=[],
    )


def payload(document_set_id):
    return {
        "document_set_id": str(document_set_id),
        "k": 5,
        "cases": [
            {
                "id": "q1",
                "query": "refund",
                "relevant_sources": ["refunds-2025.md"],
            }
        ],
    }


def test_evaluation_returns_report(monkeypatch, tmp_path):
    document_set = {"id": uuid4()}
    monkeypatch.setattr(evaluation_routes, "evaluate_cases", lambda *_args: report())

    with client_for(tmp_path, Store(document_set)) as client:
        response = client.post("/api/v1/evaluate", json=payload(document_set["id"]))

    assert response.status_code == 200
    assert response.json()["metrics"]["mrr"] == 1.0


def test_evaluation_handles_not_found_and_validation(tmp_path):
    with client_for(tmp_path, Store()) as client:
        not_found = client.post("/api/v1/evaluate", json=payload(uuid4()))
        invalid = client.post(
            "/api/v1/evaluate",
            json={"document_set_id": str(uuid4()), "cases": [], "k": 5},
        )

    assert not_found.status_code == 404
    assert invalid.status_code == 422


def test_evaluation_maps_provider_value_and_internal_errors(monkeypatch, tmp_path):
    document_set = {"id": uuid4()}

    monkeypatch.setattr(
        evaluation_routes,
        "evaluate_cases",
        lambda *_args: (_ for _ in ()).throw(EmbeddingProviderError("provider down")),
    )
    with client_for(tmp_path, Store(document_set)) as client:
        provider_response = client.post("/api/v1/evaluate", json=payload(document_set["id"]))
    assert provider_response.status_code == 503

    monkeypatch.setattr(
        evaluation_routes,
        "evaluate_cases",
        lambda *_args: (_ for _ in ()).throw(ValueError("bad evaluation")),
    )
    with client_for(tmp_path, Store(document_set)) as client:
        value_response = client.post("/api/v1/evaluate", json=payload(document_set["id"]))
    assert value_response.status_code == 400

    monkeypatch.setattr(
        evaluation_routes,
        "evaluate_cases",
        lambda *_args: (_ for _ in ()).throw(RuntimeError("failure")),
    )
    with client_for(tmp_path, Store(document_set)) as client:
        error_response = client.post("/api/v1/evaluate", json=payload(document_set["id"]))
    assert error_response.status_code == 500
