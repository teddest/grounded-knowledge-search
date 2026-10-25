from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..config import Settings, get_settings
from ..database import DatabaseDocumentStore
from ..embeddings import EmbeddingProviderError, OpenRouterEmbeddingProvider
from ..evaluation import EvaluationCase, EvaluationReport, evaluate_cases
from ..retrieval import HybridRetriever
from .ingestion import get_embedding_provider, get_store

router = APIRouter(prefix="/api/v1/evaluate", tags=["retrieval-evaluation"])


class EvaluationRequest(BaseModel):
    document_set_id: UUID
    cases: list[EvaluationCase] = Field(min_length=1)
    k: int = Field(default=5, ge=1, le=50)


@router.post("", response_model=EvaluationReport)
def evaluate(
    request: EvaluationRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    store: Annotated[DatabaseDocumentStore, Depends(get_store)],
    provider: Annotated[OpenRouterEmbeddingProvider, Depends(get_embedding_provider)],
) -> EvaluationReport:
    if store.get_document_set(request.document_set_id) is None:
        raise HTTPException(status_code=404, detail="document set not found")

    try:
        retriever = HybridRetriever(store, provider, settings)
        return evaluate_cases(retriever, request.document_set_id, request.cases, request.k)
    except EmbeddingProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="retrieval evaluation failed") from exc
