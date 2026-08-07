"""Env-driven settings. Secrets (e.g. GEMINI_API_KEY) must never be committed."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite:///./app.db"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"
    # Max PDF upload size (bytes) for /extract.
    max_upload_bytes: int = 10 * 1024 * 1024
    # Comma-separated allowlist — never use * in production demos.
    cors_origins: str = "http://localhost:5173"
    # Opt-in Buffy demo Order on startup. Leave false on Render / submission.
    seed_demo_data: bool = False

    def cors_origin_list(self) -> list[str]:
        return [part.strip() for part in self.cors_origins.split(",") if part.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
