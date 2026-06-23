import cv2
import numpy as np

from fastapi.responses import Response

from app.services.face_landmark_service import (
    FaceLandmarkService
)


class BlushService:

    async def apply(
        self,
        image_file
    ):

        landmark_service = (
            FaceLandmarkService()
        )

        data = await landmark_service.get_landmarks(
            image_file
        )

        image = data["image"]

        left_cheek = data[
            "left_cheek_points"
        ]

        right_cheek = data[
            "right_cheek_points"
        ]

        left_center = tuple(
            left_cheek.mean(
                axis=0
            ).astype(int)
        )

        right_center = tuple(
            right_cheek.mean(
                axis=0
            ).astype(int)
        )

        blush_color = (
            228,
            95,
            145
        )

        mask = np.zeros_like(
            image
        )

        cv2.circle(
            mask,
            left_center,
            35,
            blush_color,
            -1
        )

        cv2.circle(
            mask,
            right_center,
            35,
            blush_color,
            -1
        )

        mask = cv2.GaussianBlur(
            mask,
            (51, 51),
            0
        )

        output = cv2.addWeighted(
            image,
            0.8,
            mask,
            0.2,
            0
        )

        _, buffer = cv2.imencode(
            ".jpg",
            output
        )

        image_bytes = buffer.tobytes()

        return Response(
            content=image_bytes,
            media_type="image/jpeg"
        )
