from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/story_platform"
DEFAULT_ALGO = "HS256"
DEFAULT_EXPIRE_MIN = 60


class Settings(BaseSettings):
    environment: Literal["development", "production"]
    database_url: str = DEFAULT_DB_URL
    secret_key: str = Field(min_length=1)
    algorithm: str = DEFAULT_ALGO
    access_token_expire_minutes: int = DEFAULT_EXPIRE_MIN

    # The same .env file is also read by Docker Compose and therefore contains
    # POSTGRES_* variables that are not application settings.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def sql_echo(self) -> bool:
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
