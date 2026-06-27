import cv2
import numpy as np
from fastapi import HTTPException


class ImageService:
    """
    Handles image decoding.
    """

    @staticmethod
    def decode(image_bytes: bytes) -> np.ndarray:
        """
        Convert uploaded bytes into OpenCV image.
        """

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8,
        )

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR,
        )

        if image is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid or corrupted image."
            )

        return image
