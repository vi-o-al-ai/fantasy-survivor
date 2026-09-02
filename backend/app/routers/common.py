"""Shared OpenAPI pieces so clients get typed error bodies on every route."""

from typing import Any

from pydantic import BaseModel


class ErrorOut(BaseModel):
    detail: str


ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorOut, "description": "Missing or invalid bearer token"},
    403: {"model": ErrorOut, "description": "Not allowed for this user"},
    404: {"model": ErrorOut, "description": "Not found"},
    409: {"model": ErrorOut, "description": "League rule violated"},
    503: {"model": ErrorOut, "description": "Authentication not configured"},
}
