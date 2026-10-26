from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Grounded Knowledge Search API"
    database_url: str = "postgresql://search:search@localhost:5432/search"
    repository_root: str = "./documents"
    document_root: str = "documents"
    openrouter_api_key: str = ""
    openrouter_embedding_model: str = "openai/text-embedding-3-small"
    openrouter_chat_model: str = "openai/gpt-4o-mini"
    embedding_dimensions: int = 1536
    embedding_batch_size: int = 64
    retrieval_candidate_multiplier: int = 3
    answer_max_context_characters: int = 24000
    answer_max_tokens: int = 1200
    openrouter_site_url: str = "http://localhost:3000"
    openrouter_app_name: str = "grounded-knowledge-search"
    api_cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
