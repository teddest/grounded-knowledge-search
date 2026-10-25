from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Protocol
from uuid import UUID

import yaml

from .documents import DocumentMetadata, DocumentSection, SourceDocument

SUPPORTED_SUFFIXES = {".md", ".markdown", ".txt"}
SKIP_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".next",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "coverage",
}
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
FRONT_MATTER_MARKER = "---"
MAX_SECTION_CHARACTERS = 6000


class IngestionError(ValueError):
    """Raised when a document cannot be converted into a searchable record."""


class DocumentStore(Protocol):
    def start_index_run(self, document_set_id: UUID) -> UUID: ...

    def replace_document(self, document_set_id: UUID, document: SourceDocument) -> None: ...

    def complete_index_run(self, run_id: UUID, documents_seen: int, sections_seen: int) -> None: ...

    def fail_index_run(self, run_id: UUID, error_message: str) -> None: ...


def _front_matter(lines: Sequence[str]) -> tuple[dict[str, object], int]:
    if not lines or lines[0].strip() != FRONT_MATTER_MARKER:
        return {}, 0

    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as exc:
        raise IngestionError("front matter starts with '---' but has no closing marker") from exc

    try:
        raw_metadata = yaml.safe_load("\n".join(lines[1:end])) or {}
    except yaml.YAMLError as exc:
        raise IngestionError("front matter is not valid YAML") from exc
    if not isinstance(raw_metadata, dict):
        raise IngestionError("front matter must contain a mapping")
    return raw_metadata, end + 1


def _title_from_path(path: Path) -> str:
    return path.stem.replace("-", " ").replace("_", " ").strip().title()


def _metadata(path: Path, raw: dict[str, object]) -> DocumentMetadata:
    values = {"title": _title_from_path(path), **raw}
    try:
        return DocumentMetadata.model_validate(values)
    except Exception as exc:
        raise IngestionError(f"invalid metadata in {path.name}: {exc}") from exc


def _split_long_section(
    heading_path: list[str], lines: Sequence[str], start_line: int
) -> list[DocumentSection]:
    chunks: list[DocumentSection] = []
    chunk_start = 0
    while chunk_start < len(lines):
        chunk_end = chunk_start
        character_count = 0
        while chunk_end < len(lines):
            line_size = len(lines[chunk_end]) + 1
            if chunk_end > chunk_start and character_count + line_size > MAX_SECTION_CHARACTERS:
                break
            character_count += line_size
            chunk_end += 1

        content = "\n".join(lines[chunk_start:chunk_end]).strip()
        if content:
            chunks.append(
                DocumentSection(
                    ordinal=0,
                    heading_path=heading_path,
                    start_line=start_line + chunk_start,
                    end_line=start_line + chunk_end - 1,
                    content=content,
                )
            )
        chunk_start = chunk_end
    return chunks


def _number_sections(sections: Iterable[DocumentSection]) -> list[DocumentSection]:
    return [
        section.model_copy(update={"ordinal": ordinal}) for ordinal, section in enumerate(sections)
    ]


def _markdown_sections(lines: Sequence[str], content_start_line: int) -> list[DocumentSection]:
    headings = [
        (index, len(match.group(1)), match.group(2))
        for index, line in enumerate(lines)
        if (match := HEADING_PATTERN.match(line))
    ]
    sections: list[DocumentSection] = []

    if headings and headings[0][0] > 0:
        intro = _split_long_section([], lines[: headings[0][0]], content_start_line)
        sections.extend(intro)

    for heading_index, (line_index, level, heading) in enumerate(headings):
        end_index = (
            headings[heading_index + 1][0] if heading_index + 1 < len(headings) else len(lines)
        )
        heading_path = [item[2] for item in headings[: heading_index + 1] if item[1] < level]
        heading_path.append(heading)
        body = lines[line_index + 1 : end_index]
        sections.extend(
            _split_long_section(heading_path, body, content_start_line + line_index + 1)
        )

    if not headings:
        sections.extend(_split_long_section([], lines, content_start_line))
    return _number_sections(sections)


def _plain_text_sections(lines: Sequence[str], content_start_line: int) -> list[DocumentSection]:
    sections: list[DocumentSection] = []
    paragraph: list[str] = []
    paragraph_start = content_start_line

    def flush() -> None:
        nonlocal paragraph, paragraph_start
        if paragraph:
            sections.extend(_split_long_section([], paragraph, paragraph_start))
            paragraph = []

    for offset, line in enumerate(lines):
        if line.strip():
            if not paragraph:
                paragraph_start = content_start_line + offset
            paragraph.append(line)
        else:
            flush()
    flush()
    return _number_sections(sections)


def parse_document(path: Path, root: Path) -> SourceDocument:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise IngestionError(f"document is not valid UTF-8: {path}") from exc
    except OSError as exc:
        raise IngestionError(f"could not read document: {path}") from exc

    lines = text.splitlines()
    raw_metadata, content_offset = _front_matter(lines)
    metadata = _metadata(path, raw_metadata)
    content_lines = lines[content_offset:]
    content_start_line = content_offset + 1
    suffix = path.suffix.lower()
    sections = (
        _markdown_sections(content_lines, content_start_line)
        if suffix in {".md", ".markdown"}
        else _plain_text_sections(content_lines, content_start_line)
    )
    if not sections:
        raise IngestionError(f"document contains no searchable content: {path}")

    return SourceDocument(
        source_path=path.relative_to(root).as_posix(),
        metadata=metadata,
        content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        sections=sections,
    )


def discover_files(root: Path) -> list[Path]:
    if not root.exists():
        raise IngestionError(f"document root does not exist: {root}")
    if not root.is_dir():
        raise IngestionError(f"document root is not a directory: {root}")

    paths = [
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_SUFFIXES
        and not any(part in SKIP_DIRECTORIES for part in path.relative_to(root).parts)
    ]
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix())


def load_documents(root: Path) -> list[SourceDocument]:
    return [parse_document(path, root) for path in discover_files(root)]


def ingest_document_set(store: DocumentStore, document_set_id: UUID, root: Path) -> tuple[int, int]:
    run_id = store.start_index_run(document_set_id)
    try:
        documents = load_documents(root)
        for document in documents:
            store.replace_document(document_set_id, document)
        section_count = sum(len(document.sections) for document in documents)
        store.complete_index_run(run_id, len(documents), section_count)
        return len(documents), section_count
    except Exception as exc:
        store.fail_index_run(run_id, str(exc))
        raise
