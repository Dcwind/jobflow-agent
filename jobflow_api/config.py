"""Application configuration."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # API settings
    api_title: str = "Jobflow API"
    api_version: str = "0.1.0"
    debug: bool = False

    # CORS - accepts comma-separated string or JSON array
    cors_origins: list[str] = ["http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # API key for proxy authentication
    api_key: str | None = None

    # Rate limiting
    rate_limit_per_minute: int = 30

    # Database
    database_url: str = "sqlite:///./data/jobs.db"

    # Google API (for LLM features)
    google_api_key: str | None = None

    # Feature flags
    use_playwright: bool = True
    use_llm_fallback: bool = True
    use_llm_validation: bool = False  # Disabled by default to reduce API costs

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
