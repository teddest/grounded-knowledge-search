from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DocumentMetadata(BaseModel):
    model_config = ConfigDict(extra="allow")

    title: str = Field(min_length=1)
    document_id: str | None = None
    category: str | None = None
    status: str | None = None
    version: str | None = None
    effective_date: date | None = None
    audience: str | None = None
    owner: str | None = None

    @field_validator(
        "title",
        "document_id",
        "category",
        "status",
        "version",
        "audience",
        "owner",
        mode="before",
    )
    @classmethod
    def coerce_text_metadata(cls, value: object) -> object:
        return str(value) if value is not None else value

    def as_json(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude_none=True)


class DocumentSection(BaseModel):
    ordinal: int = Field(ge=0)
    heading_path: list[str] = Field(default_factory=list)
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    content: str = Field(min_length=1)


class SourceDocument(BaseModel):
    source_path: str = Field(min_length=1)
    metadata: DocumentMetadata
    content_hash: str = Field(min_length=1)
    sections: list[DocumentSection] = Field(min_length=1)


@dataclass(frozen=True)
class DiscoveredFile:
    path: str
    language: str
