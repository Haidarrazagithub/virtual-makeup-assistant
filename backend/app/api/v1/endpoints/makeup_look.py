import cv2

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form
)

from fastapi.responses import Response

from app.services.makeup_look_service import (
    MakeupLookService
)

router = APIRouter()


@router.post("/makeup-look")
async def apply_makeup(
    image: UploadFile = File(...),
    look: str = Form(...)
):

    service = MakeupLookService()

    output = await service.apply_look(
        image_file=image,
        look=look
    )

    _, buffer = cv2.imencode(
        ".jpg",
        output
    )

    return Response(
        content=buffer.tobytes(),
        media_type="image/jpeg"
    )
