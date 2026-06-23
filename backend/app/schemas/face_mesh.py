from pydantic import BaseModel


class FaceMeshResponse(BaseModel):
    face_detected: bool
    landmark_count: int
    image_width: int
    image_height: int
