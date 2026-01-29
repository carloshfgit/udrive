"""
Application Configuration

Configurações centralizadas usando Pydantic Settings.
Carrega variáveis de ambiente automaticamente.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação carregadas do ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Ambiente
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str = "postgresql+asyncpg://godrive:godrive_dev_password@localhost:5432/godrive_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Stripe
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None

    # CORS
    cors_origins: list[str] = ["*"]

    # Rate Limiting (conforme PROJECT_GUIDELINES.md)
    rate_limit_login: str = "5/minute"
    rate_limit_public: str = "30/minute"
    rate_limit_authenticated: str = "100/minute"

    # API
    api_title: str = "GoDrive API"
    api_version: str = "0.1.0"
    api_description: str = "Marketplace SaaS para conectar alunos a instrutores de direção"


@lru_cache
def get_settings() -> Settings:
    """Retorna instância cacheada das configurações."""
    return Settings()


settings = get_settings()
