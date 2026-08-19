from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/story_platform"
DEFAULT_SECRET_KEY = "ChangeMeNow"
DEFAULT_ALGO = "HS256"
DEFAULT_EXPIRE_MIN = 60


class Settings(BaseSettings):
    database_url: str = DEFAULT_DB_URL
    secret_key: str = DEFAULT_SECRET_KEY
    algorithm: str = DEFAULT_ALGO
    access_token_expire_minutes: int = DEFAULT_EXPIRE_MIN

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
