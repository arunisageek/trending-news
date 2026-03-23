from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Trending News Service", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    database_url: str = Field(default="sqlite:///./trending.db", alias="DATABASE_URL")
    redis_url: str | None = Field(default=None, alias="REDIS_URL")

    cache_ttl_seconds: int = Field(default=180, alias="CACHE_TTL_SECONDS")
    trending_lookback_hours: int = Field(default=24, alias="TRENDING_LOOKBACK_HOURS")
    trending_decay_hours: int = Field(default=12, alias="TRENDING_DECAY_HOURS")
    trending_neighbor_weight: float = Field(default=0.8, alias="TRENDING_NEIGHBOR_WEIGHT")
    bucket_cell_km: float = Field(default=10.0, alias="BUCKET_CELL_KM")
    default_radius_km: float = Field(default=25.0, alias="DEFAULT_RADIUS_KM")
    max_trending_limit: int = Field(default=20, alias="MAX_TRENDING_LIMIT")
    trending_score_window: str = Field(default="24h", alias="TRENDING_SCORE_WINDOW")
    create_tables_on_startup: bool = Field(default=False, alias="CREATE_TABLES_ON_STARTUP")


@lru_cache
def get_settings() -> Settings:
    return Settings()
