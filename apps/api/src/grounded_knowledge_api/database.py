from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from .documents import SourceDocument


@contextmanager
def connection(database_url: str) -> Iterator[psycopg.Connection[Any]]:
    database_connection = psycopg.connect(database_url, row_factory=dict_row)
    try:
        yield database_connection
        database_connection.commit()
    except Exception:
        database_connection.rollback()
        raise
    finally:
        database_connection.close()


def check_connection(database_url: str) -> bool:
    """Return whether PostgreSQL accepts a short-lived health-check connection."""
    with psycopg.connect(database_url, connect_timeout=2) as database_connection:
        database_connection.execute("SELECT 1")
    return True


def database_checker(database_url: str) -> Callable[[], bool]:
    """Create an injectable database health checker for the API boundary."""
    return lambda: check_connection(database_url)


class DatabaseDocumentStore:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def create_document_set(self, name: str, root_path: str) -> dict[str, Any]:
        with connection(self.database_url) as database_connection:
            row = database_connection.execute(
                """
                INSERT INTO document_sets (id, name, root_path)
                VALUES (%s, %s, %s)
                ON CONFLICT (root_path) DO UPDATE SET name = EXCLUDED.name
                RETURNING id, name, root_path, status, last_indexed_at, created_at
                """,
                (uuid4(), name, root_path),
            ).fetchone()
        assert row is not None
        return dict(row)

    def list_document_sets(self) -> list[dict[str, Any]]:
        with connection(self.database_url) as database_connection:
            rows = database_connection.execute(
                """
                SELECT id, name, root_path, status, last_indexed_at, created_at
                FROM document_sets
                ORDER BY created_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_document_set(self, document_set_id: UUID) -> dict[str, Any] | None:
        with connection(self.database_url) as database_connection:
            row = database_connection.execute(
                """
                SELECT id, name, root_path, status, last_indexed_at, created_at
                FROM document_sets
                WHERE id = %s
                """,
                (document_set_id,),
            ).fetchone()
        return dict(row) if row is not None else None

    def start_index_run(self, document_set_id: UUID) -> UUID:
        run_id = uuid4()
        with connection(self.database_url) as database_connection:
            database_connection.execute(
                "UPDATE document_sets SET status = 'indexing' WHERE id = %s",
                (document_set_id,),
            )
            database_connection.execute(
                "INSERT INTO index_runs (id, document_set_id, status) VALUES (%s, %s, 'running')",
                (run_id, document_set_id),
            )
        return run_id

    def replace_document(self, document_set_id: UUID, document: SourceDocument) -> None:
        now = datetime.now(UTC)
        with connection(self.database_url) as database_connection:
            existing = database_connection.execute(
                "SELECT id FROM documents WHERE document_set_id = %s AND source_path = %s",
                (document_set_id, document.source_path),
            ).fetchone()
            document_id = existing["id"] if existing is not None else uuid4()
            values = (
                document_id,
                document_set_id,
                document.source_path,
                document.metadata.title,
                document.metadata.category,
                document.metadata.status,
                document.metadata.version,
                document.metadata.effective_date,
                document.metadata.audience,
                document.metadata.owner,
                Jsonb(document.metadata.as_json()),
                document.content_hash,
                now,
            )
            if existing is None:
                database_connection.execute(
                    """
                    INSERT INTO documents
                        (id, document_set_id, source_path, title, category, status, version,
                         effective_date, audience, owner, metadata, content_hash, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    values,
                )
            else:
                database_connection.execute(
                    """
                    UPDATE documents
                    SET title = %s, category = %s, status = %s, version = %s,
                        effective_date = %s, audience = %s, owner = %s, metadata = %s,
                        content_hash = %s, updated_at = %s
                    WHERE id = %s
                    """,
                    values[3:] + (document_id,),
                )
                database_connection.execute(
                    "DELETE FROM sections WHERE document_id = %s", (document_id,)
                )

            for section in document.sections:
                searchable_text = " ".join([*section.heading_path, section.content])
                database_connection.execute(
                    """
                    INSERT INTO sections
                        (
                            document_id,
                            ordinal,
                            heading_path,
                            start_line,
                            end_line,
                            content,
                            search_vector
                        )
                    VALUES (%s, %s, %s, %s, %s, %s, to_tsvector('simple', %s))
                    """,
                    (
                        document_id,
                        section.ordinal,
                        section.heading_path,
                        section.start_line,
                        section.end_line,
                        section.content,
                        searchable_text,
                    ),
                )

    def complete_index_run(self, run_id: UUID, documents_seen: int, sections_seen: int) -> None:
        now = datetime.now(UTC)
        with connection(self.database_url) as database_connection:
            run = database_connection.execute(
                "SELECT document_set_id FROM index_runs WHERE id = %s",
                (run_id,),
            ).fetchone()
            if run is None:
                raise ValueError(f"index run not found: {run_id}")
            database_connection.execute(
                """
                UPDATE index_runs
                SET status = 'completed', documents_seen = %s, sections_seen = %s, finished_at = %s
                WHERE id = %s
                """,
                (documents_seen, sections_seen, now, run_id),
            )
            database_connection.execute(
                "UPDATE document_sets SET status = 'ready', last_indexed_at = %s WHERE id = %s",
                (now, run["document_set_id"]),
            )

    def fail_index_run(self, run_id: UUID, error_message: str) -> None:
        now = datetime.now(UTC)
        with connection(self.database_url) as database_connection:
            run = database_connection.execute(
                "SELECT document_set_id FROM index_runs WHERE id = %s",
                (run_id,),
            ).fetchone()
            if run is None:
                raise ValueError(f"index run not found: {run_id}")
            database_connection.execute(
                """
                UPDATE index_runs
                SET status = 'failed', error_message = %s, finished_at = %s
                WHERE id = %s
                """,
                (error_message[:2000], now, run_id),
            )
            database_connection.execute(
                "UPDATE document_sets SET status = 'error' WHERE id = %s",
                (run["document_set_id"],),
            )
