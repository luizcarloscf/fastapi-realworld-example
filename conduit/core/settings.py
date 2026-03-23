from functools import lru_cache
from typing import List, Literal

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    DOMAIN: str = "localhost"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    ALLOWED_CORS_ORIGINS: List[HttpUrl]
    DATABASE_URI: str
    SECRET_KEY: str
    ALGORITHM: Literal["HS256"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    OTLP_GRPC_ENDPOINT: HttpUrl


@lru_cache()
def get_settings_cached() -> Settings:
    return Settings()
