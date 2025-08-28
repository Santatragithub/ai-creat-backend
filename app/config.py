from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field, AnyUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "AI CREAT"
    API_V1_PREFIX: str = "/api/v1"
    ENV: Literal["local", "test", "dev", "prod"] = "local"
    DEBUG: bool = True

    # --- Security / Auth ---
    JWT_SECRET: str = Field("change-me-in-env", description="HS256 secret")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_IN_MIN: int = 60 * 24  # 24h

    # --- Database ---
    DATABASE_URL: str = Field(
        "postgresql+psycopg2://postgres:postgres@postgres:5432/ai_creat",
        description="SQLAlchemy URL",
    )

    # --- Message Broker / Celery ---
    RABBITMQ_URL: str = Field("amqp://guest:guest@rabbitmq:5672//")
    REDIS_URL: str = Field("redis://redis:6379/0", description="(optional) result backend")

    # Named queues (env‑driven, reviewer requirement)
    CELERY_QUEUE_PRIMARY: str = "ai_creat.jobs.primary"
    CELERY_QUEUE_PRIORITY: str = "ai_creat.jobs.priority"
    CELERY_QUEUE_DLQ: str = "ai_creat.jobs.dlq"

    # --- Storage (local by default — reviewer requirement) ---
    STORAGE_UPLOADS: str = "/data/uploads"
    STORAGE_GENERATED: str = "/data/generated"

    # Optional S3 (kept behind interface; OFF by default)
    S3_ENABLED: bool = False
    S3_BUCKET: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_ENDPOINT_URL: Optional[AnyUrl] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None

    # --- AI Provider selection (factory) ---
    # mock | openai | gemini
    AI_PROVIDER: Literal["mock", "openai", "gemini"] = "mock"
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # --- Rate limiting (optional knob) ---
    UPLOAD_MAX_FILES: int = 20
    UPLOAD_MAX_MB: int = 50

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Singleton settings (cached)."""
    return Settings()  # type: ignore[call-arg]
