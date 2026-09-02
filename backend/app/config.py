"""Application settings, loaded from the environment (or a local .env file).

Settings are read once at startup and injected where needed. Nothing else in
the app should touch ``os.environ`` directly.
"""

from functools import lru_cache
from pathlib import Path
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

    # Auth0. Issuer and JWKS URL derive from the domain.
    auth0_domain: str = ""
    auth0_audience: str = ""
    # Local-only escape hatch: verify tokens against a JWKS file on disk
    # instead of Auth0. See scripts/mint_dev_token.py. Refused when deployed.
    auth_local_jwks_file: Path | None = None
    auth_local_issuer: str = "http://localhost/dev-issuer/"

    @property
    def auth0_issuer(self) -> str:
        return f"https://{self.auth0_domain}/"

    @property
    def auth0_jwks_url(self) -> str:
        return f"https://{self.auth0_domain}/.well-known/jwks.json"

    @property
    def is_deployed(self) -> bool:
        """True when running in a real AWS environment (dev/prod)."""
        return self.app_env in ("dev", "prod")


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor; use as a FastAPI dependency."""
    return Settings()
