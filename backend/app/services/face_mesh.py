import cv2
import mediapipe as mp
import numpy as np

from fastapi import HTTPException


class FaceMeshService:

    async def analyze(self, image_file):

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

        if image is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid image uploaded"
            )

        image_rgb = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        mp_face_mesh = mp.solutions.face_mesh

        with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True
        ) as face_mesh:

            results = face_mesh.process(image_rgb)

            if not results.multi_face_landmarks:
                return {
                    "face_detected": False,
                    "landmark_count": 0
                }

            landmarks = results.multi_face_landmarks[0]

            return {
                "face_detected": True,
                "landmark_count": len(landmarks.landmark),
                "image_width": image.shape[1],
                "image_height": image.shape[0]
            }
