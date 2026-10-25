from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..answering import GroundedAnswer, GroundedAnswerService
from ..chat import ChatProviderError, OpenRouterChatProvider
from ..config import Settings, get_settings
from ..database import DatabaseDocumentStore
from ..embeddings import EmbeddingProviderError, OpenRouterEmbeddingProvider
from ..retrieval import HybridRetriever, SearchFilters
from .ingestion import get_embedding_provider, get_store

router = APIRouter(prefix="/api/v1/ask", tags=["grounded-answers"])


class AskRequest(BaseModel):
    document_set_id: UUID
    question: str = Field(min_length=1, max_length=2000)
    limit: int = Field(default=8, ge=1, le=20)
    filters: SearchFilters = Field(default_factory=SearchFilters)


def get_chat_provider(
    settings: Annotated[Settings, Depends(get_settings)],
) -> OpenRouterChatProvider:
    return OpenRouterChatProvider(settings)


@router.post("", response_model=GroundedAnswer)
def ask(
    request: AskRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    store: Annotated[DatabaseDocumentStore, Depends(get_store)],
    embedding_provider: Annotated[OpenRouterEmbeddingProvider, Depends(get_embedding_provider)],
    chat_provider: Annotated[OpenRouterChatProvider, Depends(get_chat_provider)],
) -> GroundedAnswer:
    if store.get_document_set(request.document_set_id) is None:
        raise HTTPException(status_code=404, detail="document set not found")

    try:
        retriever = HybridRetriever(store, embedding_provider, settings)
        return GroundedAnswerService(retriever, chat_provider, settings).answer(
            request.document_set_id,
            request.question,
            request.filters,
            request.limit,
        )
    except (ChatProviderError, EmbeddingProviderError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="grounded answer generation failed") from exc
