from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from grounded_knowledge_api.documents import DocumentMetadata, DocumentSection, SourceDocument
from grounded_knowledge_api.ingestion import (
    IngestionError,
    _front_matter,
    discover_files,
    ingest_document_set,
    load_documents,
    parse_document,
)


def write_file(root: Path, relative_path: str, content: str) -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_front_matter_is_optional_and_requires_mapping() -> None:
    assert _front_matter(["# Heading"])[1] == 0
    assert _front_matter(["---", "title: Example", "---", "body"])[0] == {"title": "Example"}

    with pytest.raises(IngestionError, match="no closing"):
        _front_matter(["---", "title: Example"])
    with pytest.raises(IngestionError, match="must contain a mapping"):
        _front_matter(["---", "- value", "---"])


def test_parse_markdown_preserves_metadata_headings_lines_and_hash() -> None:
    root = Path("/tmp") / f"gks-ingestion-{uuid4()}"
    root.mkdir()
    path = write_file(
        root,
        "policies/refund-policy.md",
        "---\n"
        "title: Refund Policy\n"
        "category: billing\n"
        "effective_date: 2025-02-01\n"
        "---\n"
        "Introductory text.\n\n"
        "# Refunds\n\n"
        "## Annual plans\n\n"
        "Annual customers have 30 days.\n",
    )

    document = parse_document(path, root)

    assert document.source_path == "policies/refund-policy.md"
    assert document.metadata.title == "Refund Policy"
    assert str(document.metadata.effective_date) == "2025-02-01"
    assert document.sections[0].heading_path == []
    assert document.sections[1].heading_path == ["Refunds", "Annual plans"]
    assert document.sections[1].start_line == 11
    assert len(document.content_hash) == 64


def test_parse_markdown_splits_large_sections_and_uses_fallback_title() -> None:
    root = Path("/tmp") / f"gks-ingestion-{uuid4()}"
    root.mkdir()
    content = "# Long section\n\n" + "\n".join("word " * 20 for _ in range(200))
    document = parse_document(write_file(root, "long.md", content), root)

    assert document.metadata.title == "Long"
    assert len(document.sections) > 1
    assert all(section.heading_path == ["Long section"] for section in document.sections)


def test_parse_plain_text_splits_paragraphs() -> None:
    root = Path("/tmp") / f"gks-ingestion-{uuid4()}"
    root.mkdir()
    document = parse_document(
        write_file(root, "notes.txt", "\n\nFirst line\nSecond line.\n\nSecond paragraph."), root
    )

    assert [section.content for section in document.sections] == [
        "First line\nSecond line.",
        "Second paragraph.",
    ]
    assert document.sections[1].start_line == 6


def test_parse_rejects_invalid_documents() -> None:
    root = Path("/tmp") / f"gks-ingestion-{uuid4()}"
    root.mkdir()
    with pytest.raises(IngestionError, match="not valid YAML"):
        parse_document(write_file(root, "broken.md", "---\ntitle: [unclosed\n---\n"), root)
    with pytest.raises(IngestionError, match="invalid metadata"):
        parse_document(
            write_file(root, "invalid.md", "---\neffective_date: not-a-date\n---\nBody"), root
        )
    with pytest.raises(IngestionError, match="no searchable"):
        parse_document(write_file(root, "empty.md", "---\ntitle: Empty\n---\n"), root)
    with pytest.raises(IngestionError, match="UTF-8"):
        bad = root / "bad.txt"
        bad.write_bytes(b"\xff")
        parse_document(bad, root)
    with pytest.raises(IngestionError, match="could not read"):
        parse_document(root / "missing.txt", root)


def test_discovery_is_sorted_and_skips_unsupported_and_generated_directories() -> None:
    root = Path("/tmp") / f"gks-ingestion-{uuid4()}"
    root.mkdir()
    write_file(root, "z.md", "z")
    write_file(root, "a.txt", "a")
    write_file(root, "ignored.json", "{}")
    write_file(root, "node_modules/package.md", "ignored")
    write_file(root, "openspec/proposal.md", "ignored")

    assert [path.name for path in discover_files(root)] == ["a.txt", "z.md"]
    assert len(load_documents(root)) == 2

    with pytest.raises(IngestionError, match="does not exist"):
        discover_files(root / "missing")
    file_root = root / "file.txt"
    file_root.write_text("file", encoding="utf-8")
    with pytest.raises(IngestionError, match="not a directory"):
        discover_files(file_root)


class FakeStore:
    def __init__(self, should_fail: bool = False) -> None:
        self.run_id = uuid4()
        self.should_fail = should_fail
        self.replaced: list[SourceDocument] = []
        self.completed: tuple[int, int] | None = None
        self.failed: str | None = None

    def start_index_run(self, document_set_id):
        return self.run_id

    def replace_document(self, document_set_id, document):
        if self.should_fail:
            raise RuntimeError("store failed")
        self.replaced.append(document)

    def complete_index_run(self, run_id, documents_seen, sections_seen):
        self.completed = (documents_seen, sections_seen)

    def fail_index_run(self, run_id, error_message):
        self.failed = error_message


def test_ingest_document_set_completes_and_counts_sections(tmp_path: Path) -> None:
    write_file(tmp_path, "one.md", "# One\n\nContent")
    write_file(tmp_path, "two.txt", "Two")
    store = FakeStore()

    result = ingest_document_set(store, uuid4(), tmp_path)

    assert result == (2, 2)
    assert store.completed == (2, 2)
    assert store.failed is None


def test_ingest_document_set_records_failures(tmp_path: Path) -> None:
    write_file(tmp_path, "one.md", "# One\n\nContent")
    store = FakeStore(should_fail=True)

    with pytest.raises(RuntimeError, match="store failed"):
        ingest_document_set(store, uuid4(), tmp_path)

    assert store.failed == "store failed"


def test_document_models_serialize_metadata() -> None:
    metadata = DocumentMetadata(title="Example", category="billing", version=2025.1)
    assert metadata.as_json() == {
        "title": "Example",
        "category": "billing",
        "version": "2025.1",
    }
    section = DocumentSection(ordinal=0, start_line=1, end_line=1, content="Text")
    assert section.heading_path == []
