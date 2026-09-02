"""Request-scoped accessors for app-wide services kept on ``app.state``."""

from typing import Annotated

from fastapi import Depends, Request

from app.services.league import LeagueService
from app.storage.base import Store


def get_store(request: Request) -> Store:
    store: Store = request.app.state.store
    return store


StoreDep = Annotated[Store, Depends(get_store)]


def get_league_service(store: StoreDep) -> LeagueService:
    return LeagueService(store)


LeagueDep = Annotated[LeagueService, Depends(get_league_service)]
