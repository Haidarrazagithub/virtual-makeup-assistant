from fastapi import (
    APIRouter,
    UploadFile,
    File
)

from app.services.blush_service import (
    BlushService
)

router = APIRouter()


@router.post("/apply-blush")
async def apply_blush(
    image: UploadFile = File(...)
):

    service = BlushService()

    return await service.apply(
        image
    )
