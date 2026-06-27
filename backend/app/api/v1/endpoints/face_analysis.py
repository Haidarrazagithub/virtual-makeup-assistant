from fastapi import APIRouter, File, UploadFile

from app.schemas.face_analysis import FaceAnalysisResponse
from app.services.vision.face_analysis_service import FaceAnalysisService
from app.services.vision.image_service import ImageService
from app.services.vision.image_validator import ImageValidator

router = APIRouter()

face_service = FaceAnalysisService()


@router.post(
    "/analyze-face",
    response_model=FaceAnalysisResponse,
)
async def analyze_face(
    image: UploadFile = File(...),
):

    await ImageValidator.validate(image)

    image_bytes = await image.read()

    image = ImageService.decode(image_bytes)
    context = face_service.pipeline.process(image)
    return face_service.analyze(context)
