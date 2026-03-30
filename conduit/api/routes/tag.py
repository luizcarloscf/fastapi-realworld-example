import logging

from fastapi import APIRouter, status

import conduit.services.tag as tag_service
from conduit.api.dependencies import SessionDB
from conduit.schemas.tag import TagsResponse

router = APIRouter()
log = logging.getLogger("conduit.api.tags")


@router.get(
    path="/tags",
    tags=["tags"],
    response_model=TagsResponse,
    summary="Get all tags.",
    status_code=status.HTTP_200_OK,
)
async def get_tags(session: SessionDB) -> TagsResponse:
    tags = await tag_service.get_all_tags(session=session)
    return TagsResponse(tags=[tag.name for tag in tags])
