from functools import lru_cache
from pathlib import Path
from typing import List, Literal

from pydantic import HttpUrl, computed_field
from pydantic_settings import BaseSettings
from sqlalchemy import URL


class Settings(BaseSettings):

    allowed_cors_origins: List[HttpUrl] = []
    database_user: str
    database_password: str
    database_host: str
    database_port: int
    database_name: str

    secret_key: str
    otlp_grpc_endpoint: HttpUrl
    domain: str = "localhost"
    environment: Literal["local", "staging", "production"] = "local"
    algorithm: Literal["HS256"] = "HS256"
    access_token_expire_minutes: int = 120

    class Config:
        env_file = ".env.local" if Path(".env.local").exists() else ".env"
        env_file_encoding = "utf-8"
        extra = "allow"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_uri(self) -> str:
        return URL.create(
            drivername="postgresql+psycopg_async",
            username=self.database_user,
            password=self.database_password,
            host=self.database_host,
            port=self.database_port,
            database=self.database_name,
        )


@lru_cache()
def get_settings_cached() -> Settings:
    return Settings()
