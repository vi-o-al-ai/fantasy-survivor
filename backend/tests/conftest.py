from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.auth import TokenVerifier, get_token_verifier
from app.config import Settings, get_settings
from app.main import create_app
from tests import auth_keys


@pytest.fixture
def settings() -> Settings:
    return Settings(app_env="test", log_format="console", log_level="WARNING", cors_origins=[])


@pytest.fixture
def verifier() -> TokenVerifier:
    return TokenVerifier(
        issuer=auth_keys.ISSUER, audience=auth_keys.AUDIENCE, keys=auth_keys.key_provider()
    )


@pytest.fixture
def client(settings: Settings, verifier: TokenVerifier) -> Iterator[TestClient]:
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_token_verifier] = lambda: verifier
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {auth_keys.mint_token()}"}
