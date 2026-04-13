import logging

from fastapi import APIRouter, status
from sqlmodel import select

from conduit.api.dependencies import SessionDB
from conduit.schemas.health import HealthResponse

router = APIRouter()
log = logging.getLogger("conduit.api.health")


@router.get(
    path="/health",
    tags=["health"],
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
)
async def get_health(session: SessionDB):
    query = select(1)
    await session.exec(query)
    return HealthResponse(status="ok")
