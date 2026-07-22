from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Never hardcode secrets - always use .env file!
    """

    # Database
    DATABASE_URL: str = "sqlite:///./todo.db"

    # Security - MUST be set via environment variables
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    FROM_EMAIL: str | None = None
    SMTP_USE_TLS: bool = False
    SMTP_START_TLS: bool = True

    # Application
    APP_NAME: str = "Advanced Todo List API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = []
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=PROJECT_DIR / ".env",
        env_file_encoding="utf-8",
        env_prefix="TODO_API_",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str) and not value.lstrip().startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def email_enabled(self) -> bool:
        return bool(self.SMTP_USER and self.SMTP_PASSWORD and self.FROM_EMAIL)


# Create settings instance
@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
