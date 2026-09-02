from __future__ import annotations

import logging

from app.config import Settings
from app.storage.base import Store
from app.storage.dynamodb import DynamoDBStore
from app.storage.memory import MemoryStore

log = logging.getLogger(__name__)


def build_store(settings: Settings) -> Store:
    if settings.store_backend == "dynamodb":
        log.info(
            "storage: dynamodb",
            extra={"table": settings.dynamodb_table, "endpoint": settings.dynamodb_endpoint_url},
        )
        return DynamoDBStore(
            settings.dynamodb_table,
            region=settings.aws_region,
            endpoint_url=settings.dynamodb_endpoint_url,
        )
    if settings.is_deployed:
        raise RuntimeError("STORE_BACKEND must be 'dynamodb' when deployed")
    log.warning("storage: in-memory; data is lost on restart")
    return MemoryStore()
