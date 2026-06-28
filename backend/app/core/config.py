"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==========================================================================
    # Application
    # ==========================================================================
    app_name: str = "ContractIQ AI"
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = False
    app_version: str = "1.0.0"

    # ==========================================================================
    # API
    # ==========================================================================
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # ==========================================================================
    # CORS
    # ==========================================================================
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins.",
    )

    # ==========================================================================
    # Database
    # ==========================================================================
    sqlalchemy_database_url: str

    # ==========================================================================
    # Supabase
    # ==========================================================================
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str

    storage_bucket: str = "contracts"

    # ==========================================================================
    # AI / LLM
    # ==========================================================================
    llm_provider: str = "litellm"

    llm_base_url: str
    llm_api_key: str

    llm_model: str = "gpt-4o"
    vision_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-large"

    llm_timeout_seconds: int = 120

    temperature: float = 0.2
    max_tokens: int = 4096

    # ==========================================================================
    # Document Processing
    # ==========================================================================
    max_upload_size_mb: int = 25

    supported_file_types: list[str] = Field(
        default=[
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]
    )

    chunk_size: int = 1000
    chunk_overlap: int = 200

    # ==========================================================================
    # Logging
    # ==========================================================================
    log_level: str = "INFO"

    # ==========================================================================
    # LangGraph
    # ==========================================================================
    max_agent_retries: int = 3

    # ==========================================================================
    # Environment Helpers
    # ==========================================================================
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    """Return a singleton Settings instance."""
    return Settings()