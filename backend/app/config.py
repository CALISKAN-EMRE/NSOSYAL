from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "NSosyal Pusula"
    APP_VERSION: str = "0.1.0"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://127.0.0.1:3000"

    DATA_SOURCE_TYPE: str = "json"
    DEMO_DATA_PATH: str = str(
        Path(__file__).resolve().parent.parent.parent / "data" / "demo_posts.json"
    )

    AI_EMBEDDING_PROVIDER: str = "mock"
    AI_MODERATION_PROVIDER: str = "heuristic"
    AI_RECOMMENDATION_PROVIDER: str = "rule_based"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


settings = Settings()
