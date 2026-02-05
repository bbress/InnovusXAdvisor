"""Application configuration management."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "InnovusX AI Strategy Lab"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # API
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"])

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/innovusx"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 300  # 5 minutes

    # LLM Providers
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Primary model configuration
    llm_primary_provider: Literal["openai", "anthropic"] = "openai"
    llm_primary_model: str = "gpt-4-turbo-preview"
    llm_fallback_model: str = "claude-3-sonnet-20240229"
    llm_cost_optimized_model: str = "gpt-3.5-turbo"

    # Embedding configuration
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # RAG Configuration
    rag_chunk_size: int = 512
    rag_chunk_overlap: int = 50
    rag_retrieval_k: int = 10
    rag_rerank_k: int = 5

    # Rate Limiting
    rate_limit_requests_per_minute: int = 60
    rate_limit_requests_per_hour: int = 500

    # Governance
    enable_audit_logging: bool = True
    enable_pii_detection: bool = True
    enable_bias_monitoring: bool = True
    audit_log_retention_days: int = 90

    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090

    # MLflow
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_experiment_name: str = "strategy-advisor"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance
settings = get_settings()
