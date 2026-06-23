import cv2
import mediapipe as mp
import numpy as np

from fastapi import HTTPException

from app.constants.landmarks import (
    LIPS,
    LEFT_EYE,
    RIGHT_EYE,
    LEFT_CHEEK,
    RIGHT_CHEEK
)


class FaceLandmarkService:

    async def get_landmarks(self, image_file):

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

        height, width = image.shape[:2]

        mp_face_mesh = mp.solutions.face_mesh

        with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True
        ) as face_mesh:

            results = face_mesh.process(image_rgb)

            if not results.multi_face_landmarks:
                raise HTTPException(
                    status_code=400,
                    detail="No face detected"
                )

            landmarks = results.multi_face_landmarks[0]

            lip_points = []
            left_eye_points = []
            right_eye_points = []
            left_cheek_points = []
            right_cheek_points = []
            
            for idx in LIPS:
                landmark = landmarks.landmark[idx]

                lip_points.append([
                    int(landmark.x * width),
                    int(landmark.y * height)
                ])

            for idx in LEFT_EYE:
                landmark = landmarks.landmark[idx]

                left_eye_points.append([
                    int(landmark.x * width),
                    int(landmark.y * height)
                ])

            for idx in RIGHT_EYE:
                landmark = landmarks.landmark[idx]

                right_eye_points.append([
                    int(landmark.x * width),
                    int(landmark.y * height)
                ])

            for idx in LEFT_CHEEK:
                landmark = landmarks.landmark[idx]

                left_cheek_points.append([
                    int(landmark.x * width),
                    int(landmark.y * height)
                ])

            for idx in RIGHT_CHEEK:
                landmark = landmarks.landmark[idx]

                right_cheek_points.append([
                    int(landmark.x * width),
                    int(landmark.y * height)
                ])

            return {
                "image": image,
                "lip_points": np.array(
                    lip_points,
                    dtype=np.int32
                ),
                "left_eye_points": np.array(
                    left_eye_points,
                    dtype=np.int32
                ),
                "right_eye_points": np.array(
                    right_eye_points,
                    dtype=np.int32
                ),
                "left_cheek_points": np.array(
                    left_cheek_points,
                    dtype=np.int32
                ),

                "right_cheek_points": np.array(
                    right_cheek_points,
                    dtype=np.int32
                )
            }
