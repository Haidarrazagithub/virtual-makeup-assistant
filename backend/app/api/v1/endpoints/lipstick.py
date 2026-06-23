from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form
)

from app.schemas.lipstick import (
    LipstickResponse
)

from app.services.lipstick_service import (
    LipstickService
)

router = APIRouter()


@router.post("/apply-lipstick")
async def apply_lipstick(
    image: UploadFile = File(...),
    lipstick_color: str = Form("#FF0000"),
    intensity: float = Form(0.4)
):

    service = LipstickService()

    return await service.apply(
        image,
        lipstick_color,
        intensity
    )
