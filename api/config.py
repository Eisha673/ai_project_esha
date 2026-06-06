from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    UPSTASH_REDIS_REST_URL: str = ""
    UPSTASH_REDIS_REST_TOKEN: str = ""
    QSTASH_TOKEN: str = ""
    QSTASH_CURRENT_SIGNING_KEY: str = ""
    QSTASH_NEXT_SIGNING_KEY: str = ""
    NVIDIA_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GREENHOUSE_API_KEY: str = ""
    GREENHOUSE_BASE_URL: str = "https://harvest.greenhouse.io/v3"
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    LINKEDIN_ACCESS_TOKEN: str = ""
    CALENDLY_ACCESS_TOKEN: str = ""
    CALENDLY_USER_URI: str = ""
    CALENDLY_WEBHOOK_SIGNING_KEY: str = ""
    SECRET_KEY: str = "change-me-in-production-minimum-32-chars"
    VERCEL_URL: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    @field_validator("DATABASE_URL")
    @classmethod
    def ensure_neon_ssl(cls, value: str) -> str:
        if value.startswith("postgresql") and "sslmode=" not in value:
            separator = "&" if "?" in value else "?"
            return f"{value}{separator}sslmode=require"
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
