from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Grounded Knowledge Search API"
    database_url: str = "postgresql://search:search@localhost:5432/search"
    repository_root: str = "./documents"
    openrouter_api_key: str = ""
    openrouter_embedding_model: str = "openai/text-embedding-3-small"
    openrouter_chat_model: str = "openai/gpt-4o-mini"
    embedding_dimensions: int = 1536
    api_cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
