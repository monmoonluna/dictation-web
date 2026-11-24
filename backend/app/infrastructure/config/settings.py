"""Application configuration, loaded once from the environment."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Dictation Web"
    app_env: str = "development"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    secret_key: str = "change_me_to_a_random_secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    media_storage_type: str = "local"
    media_storage_path: str = "./storage/media"
    max_upload_size_mb: int = 50

    transcriber_provider: str = "whisper"
    transcriber_model: str = "base"
    transcriber_language: str = "vi"

    log_level: str = "INFO"

    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Single shared Settings instance, resolved through dependency injection."""
    return Settings()
