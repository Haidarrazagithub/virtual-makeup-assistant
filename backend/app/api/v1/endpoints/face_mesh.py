from fastapi import APIRouter, UploadFile, File

from app.schemas.face_mesh import FaceMeshResponse
from app.services.face_mesh import FaceMeshService

router = APIRouter()


@router.post(
    "/face-mesh",
    response_model=FaceMeshResponse
)
async def face_mesh(
    image: UploadFile = File(...)
):
    service = FaceMeshService()

    return await service.analyze(image)
