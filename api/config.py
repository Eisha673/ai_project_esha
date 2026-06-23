from functools import lru_cache
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    UPSTASH_REDIS_REST_URL: str = ""
    UPSTASH_REDIS_REST_TOKEN: str = ""
    QSTASH_URL: str = "https://qstash.upstash.io"
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
    ENABLE_LIVE_AGENT_CALLS: bool = False
    SECRET_KEY: str = "change-me-in-production-minimum-32-chars"
    VERCEL_URL: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    @field_validator("DATABASE_URL")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            value = value.replace("postgresql://", "postgresql+asyncpg://", 1)
        if value.startswith("postgresql+asyncpg"):
            parts = urlsplit(value)
            query = dict(parse_qsl(parts.query, keep_blank_values=True))
            sslmode = query.pop("sslmode", None)
            if sslmode and "ssl" not in query:
                query["ssl"] = sslmode
            elif "ssl" not in query:
                query["ssl"] = "require"
            value = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
