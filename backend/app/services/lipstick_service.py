import cv2
import numpy as np

from fastapi.responses import Response

from app.utils.color import hex_to_bgr
from app.services.face_landmark_service import (
    FaceLandmarkService
)


class LipstickService:

    async def apply(
    self,
        image_file,
        lipstick_color: str,
        intensity: float
    ):

        bgr_color = hex_to_bgr(
            lipstick_color
        )

        landmark_service = (
            FaceLandmarkService()
        )

        data = await landmark_service.get_landmarks(
            image_file
        )
        image = data["image"]

        lip_points = data["lip_points"]
        lip_mask = np.zeros(
        image.shape[:2],
        dtype=np.uint8
    )

        cv2.fillPoly(
            lip_mask,
            [lip_points],
            255
        )

        lip_mask = cv2.GaussianBlur(
            lip_mask,
            (11, 11),
            0
        )
        
        lipstick_layer = np.zeros_like(
            image
        )

        lipstick_layer[:] = bgr_color
        mask_float = (
            lip_mask.astype(np.float32)
            / 255.0
        )

        mask_float = (
            mask_float * intensity
        )

        mask_float = np.expand_dims(
            mask_float,
            axis=2
        )
        
        output = (
            image.astype(np.float32)
            * (1 - mask_float)
            +
            lipstick_layer.astype(np.float32)
            * mask_float
        )

        output = output.astype(
            np.uint8
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
