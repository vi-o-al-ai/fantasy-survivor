import pytest

from app.config import Settings
from app.storage.dynamodb import DynamoDBStore
from app.storage.factory import build_store
from app.storage.memory import MemoryStore


def test_memory_by_default() -> None:
    assert isinstance(build_store(Settings(app_env="local")), MemoryStore)


def test_dynamodb_when_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "x")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "x")
    settings = Settings(
        app_env="local", store_backend="dynamodb", dynamodb_endpoint_url="http://localhost:8001"
    )
    assert isinstance(build_store(settings), DynamoDBStore)


def test_memory_refused_when_deployed() -> None:
    with pytest.raises(RuntimeError, match="STORE_BACKEND"):
        build_store(Settings(app_env="prod", store_backend="memory"))
