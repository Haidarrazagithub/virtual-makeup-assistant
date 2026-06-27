import cv2
import mediapipe as mp
import numpy as np
from fastapi import HTTPException

from app.services.vision.landmark_service import LandmarkService
from app.services.vision.skin_tone_service import SkinToneService
from app.services.vision.face_shape_service import FaceShapeService
from app.services.vision.context import VisionContext


class VisionPipeline:
    """
    Orchestrator pipeline that executes Face Mesh extraction,
    skin tone detection, and face shape classification in sequence.
    """

    def __init__(self) -> None:
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=2,  # Read up to 2 for validation
            refine_landmarks=True,
            min_detection_confidence=0.5
        )

    def process(self, image: np.ndarray) -> VisionContext:
        """
        Executes face analysis on a BGR image array.
        Returns a rich VisionContext containing coordinates, skin tone, and face shape.
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)

        if not results.multi_face_landmarks:
            raise HTTPException(
                status_code=400,
                detail="No face detected in the image."
            )

        face_count = len(results.multi_face_landmarks)
        if face_count != 1:
            raise HTTPException(
                status_code=400,
                detail="Exactly one face is required."
            )

        face_landmarks = results.multi_face_landmarks[0].landmark
        landmarks = LandmarkService.get_all_landmarks(face_landmarks)

        # Classify skin tone and face shape
        skin_tone = SkinToneService.detect_skin_tone(image, landmarks)
        face_shape = FaceShapeService.detect_face_shape(landmarks)
        regions = LandmarkService.get_regions(landmarks)

        return VisionContext(
            original_image=image,
            rgb_image=rgb_image,
            landmarks=landmarks,
            regions=regions,
            skin_tone=skin_tone,
            face_shape=face_shape,
            face_count=face_count
        )
