import cv2
import mediapipe as mp
import numpy as np
from fastapi import HTTPException

from app.schemas.face_analysis import FaceAnalysisResponse


class FaceAnalysisService:
    """
    Performs face detection using MediaPipe Face Mesh.
    """

    def __init__(self) -> None:

        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=2,
            refine_landmarks=True,
            min_detection_confidence=0.5,
        )

    def analyze(
        self,
        image: np.ndarray,
    ) -> FaceAnalysisResponse:

        rgb_image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB,
        )

        results = self.face_mesh.process(rgb_image)

        if not results.multi_face_landmarks:
            raise HTTPException(
                status_code=400,
                detail="No face detected."
            )

        face_count = len(results.multi_face_landmarks)

        if face_count != 1:
            raise HTTPException(
                status_code=400,
                detail="Exactly one face is required."
            )

        return FaceAnalysisResponse(
            face_detected=True,
            face_count=1,
        )
