from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import create_app


@pytest.fixture
def settings() -> Settings:
    return Settings(app_env="test", log_format="console", log_level="WARNING", cors_origins=[])


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as c:
        yield c
