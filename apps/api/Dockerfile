FROM ghcr.io/astral-sh/uv:0.13.1 AS uv
FROM python:3.12.13-slim-bookworm

COPY --from=uv /uv /uvx /bin/

WORKDIR /workspace/apps/api
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/workspace/apps/api/.venv

COPY apps/api/pyproject.toml apps/api/uv.lock ./
RUN uv sync --locked

COPY apps/api/src ./src

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "grounded_knowledge_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/workspace/apps/api/src"]
