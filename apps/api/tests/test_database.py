from __future__ import annotations

from contextlib import contextmanager
from datetime import date
from unittest.mock import Mock
from uuid import uuid4

import pytest

from grounded_knowledge_api import database
from grounded_knowledge_api.documents import DocumentMetadata, DocumentSection, SourceDocument


class Result:
    def __init__(self, one=None, many=None):
        self.one = one
        self.many = many or []

    def fetchone(self):
        return self.one

    def fetchall(self):
        return self.many


class FakeConnection:
    def __init__(self, results=None):
        self.results = iter(results or [])
        self.calls = []

    def execute(self, query, params=()):
        self.calls.append((query, params))
        return next(self.results, Result())


@contextmanager
def patched_connection(connection):
    yield connection


def source_document() -> SourceDocument:
    return SourceDocument(
        source_path="policies/refunds.md",
        metadata=DocumentMetadata(
            title="Refunds", category="billing", effective_date=date(2025, 1, 1)
        ),
        content_hash="hash",
        sections=[
            DocumentSection(
                ordinal=0,
                heading_path=["Refunds"],
                start_line=2,
                end_line=3,
                content="Refunds are available.",
            )
        ],
    )


def test_connection_commits_and_closes(monkeypatch):
    fake = Mock()
    monkeypatch.setattr(database.psycopg, "connect", Mock(return_value=fake))
    monkeypatch.setattr(database, "register_vector", Mock())

    with database.connection("postgresql://example") as connection:
        assert connection is fake

    fake.commit.assert_called_once_with()
    fake.close.assert_called_once_with()


def test_connection_rolls_back_and_closes_on_error(monkeypatch):
    fake = Mock()
    monkeypatch.setattr(database.psycopg, "connect", Mock(return_value=fake))
    monkeypatch.setattr(database, "register_vector", Mock())

    with pytest.raises(RuntimeError, match="boom"):
        with database.connection("postgresql://example"):
            raise RuntimeError("boom")

    fake.rollback.assert_called_once_with()
    fake.close.assert_called_once_with()


def test_document_set_crud(monkeypatch):
    row = {"id": uuid4(), "name": "Example", "root_path": ".", "status": "registered"}
    store = database.DatabaseDocumentStore("postgresql://example")

    create_connection = FakeConnection([Result(one=row)])
    monkeypatch.setattr(database, "connection", lambda _url: patched_connection(create_connection))
    assert store.create_document_set("Example", ".") == row

    list_connection = FakeConnection([Result(many=[row])])
    monkeypatch.setattr(database, "connection", lambda _url: patched_connection(list_connection))
    assert store.list_document_sets() == [row]

    found_connection = FakeConnection([Result(one=row)])
    monkeypatch.setattr(database, "connection", lambda _url: patched_connection(found_connection))
    assert store.get_document_set(row["id"]) == row

    missing_connection = FakeConnection([Result(one=None)])
    monkeypatch.setattr(database, "connection", lambda _url: patched_connection(missing_connection))
    assert store.get_document_set(uuid4()) is None


def test_index_run_lifecycle(monkeypatch):
    store = database.DatabaseDocumentStore("postgresql://example")
    document_set_id = uuid4()
    run_id = uuid4()

    start_connection = FakeConnection()
    monkeypatch.setattr(database, "connection", lambda _url: patched_connection(start_connection))
    actual_run_id = store.start_index_run(document_set_id)
    assert actual_run_id is not None
    assert len(start_connection.calls) == 2

    complete_connection = FakeConnection([Result(one={"document_set_id": document_set_id})])
    monkeypatch.setattr(
        database, "connection", lambda _url: patched_connection(complete_connection)
    )
    store.complete_index_run(run_id, 2, 4)
    assert len(complete_connection.calls) == 3

    fail_connection = FakeConnection([Result(one={"document_set_id": document_set_id})])
    monkeypatch.setattr(database, "connection", lambda _url: patched_connection(fail_connection))
    store.fail_index_run(run_id, "failure")
    assert len(fail_connection.calls) == 3

    missing_complete = FakeConnection([Result(one=None)])
    monkeypatch.setattr(database, "connection", lambda _url: patched_connection(missing_complete))
    with pytest.raises(ValueError, match="index run not found"):
        store.complete_index_run(run_id, 0, 0)

    missing_fail = FakeConnection([Result(one=None)])
    monkeypatch.setattr(database, "connection", lambda _url: patched_connection(missing_fail))
    with pytest.raises(ValueError, match="index run not found"):
        store.fail_index_run(run_id, "failure")


def test_embedding_section_queries_and_updates(monkeypatch):
    store = database.DatabaseDocumentStore("postgresql://example")
    row = {"id": 1, "content": "text", "source_path": "one.md"}
    select_connection = FakeConnection([Result(many=[row])])
    monkeypatch.setattr(database, "connection", lambda _url: patched_connection(select_connection))

    assert store.pending_embedding_sections(uuid4(), "model") == [row]

    update_connection = FakeConnection()
    monkeypatch.setattr(database, "connection", lambda _url: patched_connection(update_connection))
    store.update_section_embeddings([(1, [0.1, 0.2], "model", "hash")])
    assert "UPDATE sections" in update_connection.calls[0][0]


def test_replace_document_inserts_new_document(monkeypatch):
    store = database.DatabaseDocumentStore("postgresql://example")
    connection = FakeConnection([Result(one=None)])
    monkeypatch.setattr(database, "connection", lambda _url: patched_connection(connection))

    store.replace_document(uuid4(), source_document())

    assert len(connection.calls) == 3
    assert "INSERT INTO documents" in connection.calls[1][0]
    assert "INSERT INTO sections" in connection.calls[2][0]


def test_replace_document_updates_existing_document(monkeypatch):
    store = database.DatabaseDocumentStore("postgresql://example")
    document_id = uuid4()
    connection = FakeConnection([Result(one={"id": document_id})])
    monkeypatch.setattr(database, "connection", lambda _url: patched_connection(connection))

    store.replace_document(uuid4(), source_document())

    assert len(connection.calls) == 4
    assert "UPDATE documents" in connection.calls[1][0]
    assert "DELETE FROM sections" in connection.calls[2][0]
    assert "INSERT INTO sections" in connection.calls[3][0]
