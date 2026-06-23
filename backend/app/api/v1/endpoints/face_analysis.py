from fastapi import APIRouter

from app.schemas.face import FaceAnalysisResponse
from app.services.face_detection import FaceDetectionService

router = APIRouter()


@router.post(
    "/analyze-face",
    response_model=FaceAnalysisResponse
)
def analyze_face():

    service = FaceDetectionService()

    return service.analyze()
