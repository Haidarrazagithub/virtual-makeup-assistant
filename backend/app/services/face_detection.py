import cv2
import mediapipe as mp
import numpy as np

from fastapi import HTTPException


class FaceDetectionService:

    async def analyze(self, image_file):

        # Validate file type
        if not image_file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="Only image files are allowed"
            )

        contents = await image_file.read()

        np_image = np.frombuffer(
            contents,
            np.uint8
        )

        image = cv2.imdecode(
            np_image,
            cv2.IMREAD_COLOR
        )

        # Validate image
        if image is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid image uploaded"
            )

        image_rgb = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        mp_face = mp.solutions.face_detection

        with mp_face.FaceDetection(
            model_selection=0,
            min_detection_confidence=0.5
        ) as detector:

            results = detector.process(image_rgb)

            count = 0

            if results.detections:
                count = len(results.detections)

            return {
                "face_detected": count > 0,
                "face_count": count,
                "image_width": image.shape[1],
                "image_height": image.shape[0]
            }
