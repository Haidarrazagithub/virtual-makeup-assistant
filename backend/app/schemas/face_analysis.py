from pydantic import BaseModel


class FaceAnalysisResponse(BaseModel):
    face_detected: bool
    face_count: int
