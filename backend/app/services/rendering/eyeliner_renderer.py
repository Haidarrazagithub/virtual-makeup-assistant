import cv2
import numpy as np
from app.utils.color import hex_to_bgr


class EyelinerRenderer:
    """
    Renders clean eyeliner contours using Multiply Blend Mode.
    """

    def apply(
        self,
        image: np.ndarray,
        left_eye_contour: np.ndarray,
        right_eye_contour: np.ndarray,
        color: str = "#000000",
        intensity: float = 0.6
    ) -> np.ndarray:
        if not color or intensity <= 0.0:
            return image

        bgr_color = hex_to_bgr(color)
        intensity = min(intensity, 0.7)  # Cap at 70%

        h, w = image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)

        cv2.polylines(mask, [left_eye_contour], isClosed=False, color=255, thickness=2)
        cv2.polylines(mask, [right_eye_contour], isClosed=False, color=255, thickness=2)

        mask = cv2.GaussianBlur(mask, (3, 3), 0)

        # Multiply blend
        image_float = image.astype(float)
        color_img = np.full_like(image, bgr_color, dtype=np.uint8)
        multiply_blended = (image_float * color_img.astype(float)) / 255.0

        mask_3d = np.expand_dims(mask.astype(float) / 255.0, axis=2)
        final_liner = image_float * (1.0 - mask_3d * intensity) + multiply_blended * (mask_3d * intensity)
        return np.clip(final_liner, 0, 255).astype(np.uint8)
