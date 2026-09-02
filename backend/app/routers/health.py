from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import Settings, get_settings

router = APIRouter(tags=["health"])

SettingsDep = Annotated[Settings, Depends(get_settings)]


class HealthResponse(BaseModel):
    status: str
    env: str


@router.get("/health", response_model=HealthResponse)
def health(settings: SettingsDep) -> HealthResponse:
    return HealthResponse(status="ok", env=settings.app_env)
