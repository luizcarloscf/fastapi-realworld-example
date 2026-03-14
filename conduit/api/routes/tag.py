from fastapi import APIRouter

import conduit.crud.tag as crud_tags
from conduit.api.deps import SessionDB
from conduit.schemas.tag import TagsResponse

router = APIRouter()


@router.get(
    path="/tags",
    tags=["tags"],
    response_model=TagsResponse,
    summary="Get all tags.",
)
async def get_tags(session: SessionDB) -> TagsResponse:
    tags = await crud_tags.get_all_tags(session=session)
    return TagsResponse(tags=[tag.name for tag in tags])
