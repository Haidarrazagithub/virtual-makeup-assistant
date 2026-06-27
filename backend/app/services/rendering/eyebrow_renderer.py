import cv2
import numpy as np
from app.utils.color import hex_to_bgr


class EyebrowRenderer:
    """
    Renders eyebrows with Multiply Blend Mode to keep natural hair details.
    """

    def apply(
        self,
        image: np.ndarray,
        left_eb_pts: np.ndarray,
        right_eb_pts: np.ndarray,
        color: str = "#2C1E1A",
        intensity: float = 0.4
    ) -> np.ndarray:
        if not color or intensity <= 0.0:
            return image

        bgr_color = hex_to_bgr(color)
        intensity = min(intensity, 0.25)

        h, w = image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [left_eb_pts], 255)
        cv2.fillPoly(mask, [right_eb_pts], 255)

        mask = cv2.GaussianBlur(mask, (3, 3), 0)

        # Multiply blend
        image_float = image.astype(float)
        color_img = np.full_like(image, bgr_color, dtype=np.uint8)
        multiply_blended = (image_float * color_img.astype(float)) / 255.0

        mask_3d = np.expand_dims(mask.astype(float) / 255.0, axis=2)
        final_eb = image_float * (1.0 - mask_3d * intensity) + multiply_blended * (mask_3d * intensity)
        return np.clip(final_eb, 0, 255).astype(np.uint8)
