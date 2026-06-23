from fastapi import APIRouter, UploadFile, File

from app.schemas.face import FaceAnalysisResponse
from app.services.face_detection import FaceDetectionService

router = APIRouter()


@router.post(
    "/analyze-face",
    response_model=FaceAnalysisResponse
)
async def analyze_face(
    image: UploadFile = File(...)
):

    service = FaceDetectionService()

    return await service.analyze(image)
