from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.auth import TokenVerifier, get_token_verifier
from app.config import Settings, get_settings
from app.main import create_app
from app.storage.memory import MemoryStore
from tests import auth_keys
from tests.auth_keys import mint_token


@pytest.fixture
def settings() -> Settings:
    return Settings(app_env="test", log_format="console", log_level="WARNING", cors_origins=[])


@pytest.fixture
def verifier() -> TokenVerifier:
    return TokenVerifier(
        issuer=auth_keys.ISSUER, audience=auth_keys.AUDIENCE, keys=auth_keys.key_provider()
    )


@pytest.fixture
def store() -> MemoryStore:
    return MemoryStore()


@pytest.fixture
def client(settings: Settings, verifier: TokenVerifier, store: MemoryStore) -> Iterator[TestClient]:
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_token_verifier] = lambda: verifier
    app.state.store = store
    with TestClient(app) as c:
        yield c


def bearer(**claims: object) -> dict[str, str]:
    return {"Authorization": f"Bearer {mint_token(**claims)}"}  # type: ignore[arg-type]


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """A plain logged-in player."""
    return bearer(sub="auth0|player1")


@pytest.fixture
def admin_headers() -> dict[str, str]:
    """A commissioner who can manage seasons and enter stats."""
    return bearer(sub="auth0|admin", permissions=["manage:seasons", "write:stats"])
