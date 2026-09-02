from fastapi import APIRouter
from pydantic import BaseModel

from app.auth import CurrentUserDep

router = APIRouter(tags=["me"])


class MeResponse(BaseModel):
    sub: str
    email: str | None
    permissions: list[str]


@router.get("/me", response_model=MeResponse)
def me(user: CurrentUserDep) -> MeResponse:
    return MeResponse(sub=user.sub, email=user.email, permissions=sorted(user.permissions))
