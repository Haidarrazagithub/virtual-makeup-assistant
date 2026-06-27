import cv2
import mediapipe as mp
import numpy as np
from fastapi import HTTPException

from app.schemas.face_analysis import FaceAnalysisResponse
from app.services.vision.landmark_service import LandmarkService

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

        face_landmarks = results.multi_face_landmarks[0].landmark
        landmarks = LandmarkService.get_all_landmarks(
            face_landmarks
        )

        # Extract regions internally as requested by the pipeline
        lips = LandmarkService.get_lips(landmarks)
        left_eye = LandmarkService.get_left_eye(landmarks)
        right_eye = LandmarkService.get_right_eye(landmarks)
        face_outline = LandmarkService.get_face_outline(landmarks)
        left_eyebrow = LandmarkService.get_left_eyebrow(landmarks)
        right_eyebrow = LandmarkService.get_right_eyebrow(landmarks)

        # Detect skin tone
        from app.services.vision.skin_tone_service import SkinToneService
        skin_tone = SkinToneService.detect_skin_tone(image, landmarks)

        # Detect face shape
        from app.services.vision.face_shape_service import FaceShapeService
        face_shape = FaceShapeService.detect_face_shape(landmarks)

        # Get presets for detected skin tone
        from app.constants.presets import PRESETS
        recommended = PRESETS.get(skin_tone)

        return FaceAnalysisResponse(
            face_detected=True,
            face_count=1,
            landmark_count=len(landmarks),
            skin_tone=skin_tone,
            face_shape=face_shape,
            recommended_presets=recommended
        )

