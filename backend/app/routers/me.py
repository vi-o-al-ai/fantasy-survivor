from fastapi import APIRouter
from pydantic import BaseModel

from app.auth import CurrentUserDep
from app.routers.common import ERROR_RESPONSES

router = APIRouter(tags=["me"], responses=ERROR_RESPONSES)


class MeResponse(BaseModel):
    sub: str
    email: str | None
    permissions: list[str]


@router.get("/me", response_model=MeResponse)
def me(user: CurrentUserDep) -> MeResponse:
    return MeResponse(sub=user.sub, email=user.email, permissions=sorted(user.permissions))
