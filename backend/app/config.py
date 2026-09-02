"""Application settings, loaded from the environment (or a local .env file).

Settings are read once at startup and injected where needed. Nothing else in
the app should touch ``os.environ`` directly.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["local", "test", "dev", "prod"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "fantasy-survivor-api"
    app_env: Environment = "local"
    log_level: str = "INFO"
    log_format: Literal["console", "json"] = "json"
    cors_origins: list[str] = []

    @property
    def is_deployed(self) -> bool:
        """True when running in a real AWS environment (dev/prod)."""
        return self.app_env in ("dev", "prod")


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor; use as a FastAPI dependency."""
    return Settings()
