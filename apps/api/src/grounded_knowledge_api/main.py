from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings, get_settings
from .database import database_checker


def get_database_health_checker(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Callable[[], bool]:
    return database_checker(settings.database_url)


def create_app(settings: Settings | None = None) -> FastAPI:
    application_settings = settings or get_settings()
    application = FastAPI(
        title="Grounded Knowledge Search API",
        version="0.1.0",
        description="Document ingestion, retrieval, grounded answers, and evaluation.",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=application_settings.api_cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @application.get("/health")
    def health(
        database_is_healthy: Annotated[Callable[[], bool], Depends(get_database_health_checker)],
    ) -> dict[str, str]:
        try:
            database_is_healthy()
        except Exception as exc:
            raise HTTPException(status_code=503, detail="database unavailable") from exc
        return {"status": "ok", "database": "ok"}

    @application.get("/api/v1/health")
    def versioned_health(
        database_is_healthy: Annotated[Callable[[], bool], Depends(get_database_health_checker)],
    ) -> dict[str, str]:
        return health(database_is_healthy)

    return application


app = create_app()
