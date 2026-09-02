"""Request-scoped accessors for app-wide services kept on ``app.state``."""

from typing import Annotated

from fastapi import Depends, Request

from app.storage.base import Store


def get_store(request: Request) -> Store:
    store: Store = request.app.state.store
    return store


StoreDep = Annotated[Store, Depends(get_store)]
