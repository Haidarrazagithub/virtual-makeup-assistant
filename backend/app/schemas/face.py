from pydantic import BaseModel


class FaceAnalysisResponse(BaseModel):
    face_detected: bool
    face_count: int
    image_width: int
    image_height: int
