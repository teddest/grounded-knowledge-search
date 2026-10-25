from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..config import Settings, get_settings
from ..database import DatabaseDocumentStore
from ..embeddings import EmbeddingProviderError, OpenRouterEmbeddingProvider
from ..retrieval import HybridRetriever, SearchFilters, SearchResult
from .ingestion import get_embedding_provider, get_store

router = APIRouter(prefix="/api/v1/search", tags=["retrieval"])


class SearchRequest(BaseModel):
    document_set_id: UUID
    query: str = Field(min_length=1, max_length=2000)
    limit: int = Field(default=10, ge=1, le=50)
    filters: SearchFilters = Field(default_factory=SearchFilters)


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


@router.post("", response_model=SearchResponse)
def search(
    request: SearchRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    store: Annotated[DatabaseDocumentStore, Depends(get_store)],
    provider: Annotated[OpenRouterEmbeddingProvider, Depends(get_embedding_provider)],
) -> SearchResponse:
    if store.get_document_set(request.document_set_id) is None:
        raise HTTPException(status_code=404, detail="document set not found")

    try:
        results = HybridRetriever(store, provider, settings).search(
            request.document_set_id,
            request.query,
            request.filters,
            request.limit,
        )
    except EmbeddingProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="search failed") from exc

    return SearchResponse(query=request.query, results=results)
