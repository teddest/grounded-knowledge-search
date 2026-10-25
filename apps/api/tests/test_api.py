from collections.abc import Callable
from unittest.mock import Mock

from fastapi.testclient import TestClient

from grounded_knowledge_api.config import Settings, get_settings
from grounded_knowledge_api.database import check_connection, database_checker
from grounded_knowledge_api.main import create_app, get_database_health_checker


def test_health_endpoints_report_database_health() -> None:
    app = create_app(Settings(api_cors_origins=[]))
    app.dependency_overrides[get_database_health_checker] = lambda: lambda: True

    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok", "database": "ok"}
        assert client.get("/api/v1/health").status_code == 200


def test_health_endpoint_reports_database_failure() -> None:
    app = create_app(Settings(api_cors_origins=[]))
    app.dependency_overrides[get_database_health_checker] = lambda: lambda: _raise_database_error()

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"detail": "database unavailable"}


def _raise_database_error() -> bool:
    raise RuntimeError("database is down")


def test_database_checker_uses_configured_database_url(monkeypatch) -> None:
    connection = Mock()
    connection.__enter__ = Mock(return_value=connection)
    connection.__exit__ = Mock(return_value=None)
    execute = connection.execute
    connect = Mock(return_value=connection)
    monkeypatch.setattr("grounded_knowledge_api.database.psycopg.connect", connect)

    assert check_connection("postgresql://example") is True
    connect.assert_called_once_with("postgresql://example", connect_timeout=2)
    execute.assert_called_once_with("SELECT 1")


def test_database_checker_factory_returns_callable(monkeypatch) -> None:
    monkeypatch.setattr(
        "grounded_knowledge_api.database.check_connection",
        lambda url: url == "postgresql://healthy",
    )
    checker: Callable[[], bool] = database_checker("postgresql://healthy")

    assert checker() is True


def test_settings_dependency_is_cached() -> None:
    get_settings.cache_clear()
    first = get_settings()
    second = get_settings()

    assert first is second
    assert first.embedding_dimensions == 1536


def test_database_dependency_builds_checker() -> None:
    checker = get_database_health_checker(Settings(database_url="postgresql://example"))

    assert callable(checker)
