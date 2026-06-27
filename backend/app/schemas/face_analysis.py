from pydantic import BaseModel
from typing import Optional, Dict, Any


class FaceAnalysisResponse(BaseModel):
    face_detected: bool
    face_count: int
    landmark_count: int
    skin_tone: Optional[str] = None
    face_shape: Optional[str] = None
    recommended_presets: Optional[Dict[str, Any]] = None


