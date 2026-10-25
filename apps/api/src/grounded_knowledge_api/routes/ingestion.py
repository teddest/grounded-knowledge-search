from __future__ import annotations

from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..config import Settings, get_settings
from ..database import DatabaseDocumentStore
from ..embeddings import EmbeddingProviderError, OpenRouterEmbeddingProvider
from ..indexing import EmbeddingIndexingService
from ..ingestion import IngestionError, ingest_document_set

router = APIRouter(prefix="/api/v1/document-sets", tags=["document-ingestion"])


class DocumentSetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    path: str = Field(default=".", min_length=1, max_length=500)


class DocumentSetResponse(BaseModel):
    id: UUID
    name: str
    root_path: str
    status: str


class IngestionResponse(BaseModel):
    document_set_id: UUID
    status: str
    documents_seen: int
    sections_seen: int


class EmbeddingResponse(BaseModel):
    document_set_id: UUID
    status: str
    sections_seen: int
    sections_embedded: int


def get_store(settings: Annotated[Settings, Depends(get_settings)]) -> DatabaseDocumentStore:
    return DatabaseDocumentStore(settings.database_url)


def resolve_document_root(configured_root: str, requested_path: str) -> Path:
    root = Path(configured_root).expanduser().resolve()
    candidate = (root / requested_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise IngestionError(
            "document path must remain inside the configured repository root"
        ) from exc
    if not candidate.is_dir():
        raise IngestionError(f"document path is not a directory: {requested_path}")
    return candidate


def get_embedding_provider(
    settings: Annotated[Settings, Depends(get_settings)],
) -> OpenRouterEmbeddingProvider:
    return OpenRouterEmbeddingProvider(settings)


def _document_set_response(row: dict[str, object]) -> DocumentSetResponse:
    return DocumentSetResponse(
        id=row["id"],  # type: ignore[arg-type]
        name=str(row["name"]),
        root_path=str(row["root_path"]),
        status=str(row["status"]),
    )


@router.post("", response_model=DocumentSetResponse, status_code=status.HTTP_201_CREATED)
def create_document_set(
    request: DocumentSetCreate,
    settings: Annotated[Settings, Depends(get_settings)],
    store: Annotated[DatabaseDocumentStore, Depends(get_store)],
) -> DocumentSetResponse:
    normalized_path = request.path.strip("/") or "."
    try:
        resolve_document_root(settings.repository_root, normalized_path)
    except IngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _document_set_response(store.create_document_set(request.name, normalized_path))


@router.get("", response_model=list[DocumentSetResponse])
def list_document_sets(
    store: Annotated[DatabaseDocumentStore, Depends(get_store)],
) -> list[DocumentSetResponse]:
    return [_document_set_response(row) for row in store.list_document_sets()]


@router.post("/{document_set_id}/ingest", response_model=IngestionResponse)
def ingest(
    document_set_id: UUID,
    settings: Annotated[Settings, Depends(get_settings)],
    store: Annotated[DatabaseDocumentStore, Depends(get_store)],
) -> IngestionResponse:
    document_set = store.get_document_set(document_set_id)
    if document_set is None:
        raise HTTPException(status_code=404, detail="document set not found")

    try:
        root = resolve_document_root(settings.repository_root, str(document_set["root_path"]))
        documents_seen, sections_seen = ingest_document_set(store, document_set_id, root)
    except IngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="document ingestion failed") from exc

    return IngestionResponse(
        document_set_id=document_set_id,
        status="ready",
        documents_seen=documents_seen,
        sections_seen=sections_seen,
    )


@router.post("/{document_set_id}/index", response_model=EmbeddingResponse)
def index_embeddings(
    document_set_id: UUID,
    settings: Annotated[Settings, Depends(get_settings)],
    store: Annotated[DatabaseDocumentStore, Depends(get_store)],
    provider: Annotated[OpenRouterEmbeddingProvider, Depends(get_embedding_provider)],
) -> EmbeddingResponse:
    if store.get_document_set(document_set_id) is None:
        raise HTTPException(status_code=404, detail="document set not found")

    try:
        sections_seen, sections_embedded = EmbeddingIndexingService(
            store, provider, settings
        ).index_document_set(document_set_id)
    except EmbeddingProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="embedding indexing failed") from exc

    return EmbeddingResponse(
        document_set_id=document_set_id,
        status="ready",
        sections_seen=sections_seen,
        sections_embedded=sections_embedded,
    )
