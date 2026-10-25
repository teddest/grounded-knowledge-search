from __future__ import annotations

import re
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from .documents import SourceDocument


@contextmanager
def connection(database_url: str) -> Iterator[psycopg.Connection[Any]]:
    database_connection = psycopg.connect(database_url, row_factory=dict_row)
    register_vector(database_connection)
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

    @staticmethod
    def _document_filter_sql(
        document_set_id: UUID,
        category: str | None,
        status: str | None,
        version: str | None,
    ) -> tuple[str, list[Any]]:
        clauses = ["d.document_set_id = %s"]
        params: list[Any] = [document_set_id]
        for column, value in (("category", category), ("status", status), ("version", version)):
            if value is not None:
                clauses.append(f"d.{column} = %s")
                params.append(value)
        return " AND ".join(clauses), params

    def vector_search(
        self,
        document_set_id: UUID,
        embedding: list[float],
        limit: int,
        category: str | None = None,
        status: str | None = None,
        version: str | None = None,
    ) -> list[dict[str, Any]]:
        filters, filter_params = self._document_filter_sql(
            document_set_id, category, status, version
        )
        query = f"""
            SELECT s.id, d.source_path, d.title, d.category, d.status, d.version,
                   d.effective_date, s.heading_path, s.start_line, s.end_line, s.content,
                   1 - (s.embedding <=> %s) AS similarity
            FROM sections AS s
            JOIN documents AS d ON d.id = s.document_id
            WHERE {filters} AND s.embedding IS NOT NULL
            ORDER BY s.embedding <=> %s
            LIMIT %s
        """
        with connection(self.database_url) as database_connection:
            rows = database_connection.execute(
                query, [Vector(embedding), *filter_params, Vector(embedding), limit]
            ).fetchall()
        return [dict(row) for row in rows]

    def lexical_search(
        self,
        document_set_id: UUID,
        query: str,
        limit: int,
        category: str | None = None,
        status: str | None = None,
        version: str | None = None,
    ) -> list[dict[str, Any]]:
        filters, filter_params = self._document_filter_sql(
            document_set_id, category, status, version
        )
        terms = re.findall(r"[A-Za-z0-9_]+", query)
        if not terms:
            return []
        lexical_query = " | ".join(terms)
        sql = f"""
            SELECT s.id, d.source_path, d.title, d.category, d.status, d.version,
                   d.effective_date, s.heading_path, s.start_line, s.end_line, s.content,
                   ts_rank_cd(s.search_vector, to_tsquery('simple', %s)) AS lexical_score
            FROM sections AS s
            JOIN documents AS d ON d.id = s.document_id
            WHERE {filters}
              AND (
                s.search_vector @@ to_tsquery('simple', %s)
                OR lower(d.title) LIKE lower(%s)
                OR lower(d.source_path) LIKE lower(%s)
              )
            ORDER BY lexical_score DESC, s.id
            LIMIT %s
        """
        wildcard = f"%{query}%"
        with connection(self.database_url) as database_connection:
            rows = database_connection.execute(
                sql,
                [lexical_query, *filter_params, lexical_query, wildcard, wildcard, limit],
            ).fetchall()
        return [dict(row) for row in rows]

    def pending_embedding_sections(
        self, document_set_id: UUID, embedding_model: str
    ) -> list[dict[str, Any]]:
        with connection(self.database_url) as database_connection:
            rows = database_connection.execute(
                """
                SELECT s.id, s.content, s.heading_path, s.start_line, s.end_line,
                       d.source_path, d.title, d.category, d.status, d.version,
                       d.effective_date
                FROM sections AS s
                JOIN documents AS d ON d.id = s.document_id
                WHERE d.document_set_id = %s
                  AND (s.embedding IS NULL OR s.embedding_model IS DISTINCT FROM %s)
                ORDER BY d.source_path, s.ordinal
                """,
                (document_set_id, embedding_model),
            ).fetchall()
        return [dict(row) for row in rows]

    def update_section_embeddings(
        self,
        embeddings: list[tuple[int, list[float], str, str]],
    ) -> None:
        with connection(self.database_url) as database_connection:
            for section_id, embedding, model, input_hash in embeddings:
                database_connection.execute(
                    """
                    UPDATE sections
                    SET embedding = %s, embedding_model = %s, embedding_input_hash = %s
                    WHERE id = %s
                    """,
                    (Vector(embedding), model, input_hash, section_id),
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
