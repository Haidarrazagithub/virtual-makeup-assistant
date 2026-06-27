import cv2
import numpy as np
from app.utils.color import hex_to_bgr


class LipstickRenderer:
    """
    Renders custom lipstick tint onto upper and lower lips.
    """

    def apply(
        self,
        image: np.ndarray,
        upper_lip_pts: np.ndarray,
        lower_lip_pts: np.ndarray,
        color: str = "#FF0000",
        intensity: float = 0.4
    ) -> np.ndarray:
        if not color or intensity <= 0.0:
            return image

        bgr_color = hex_to_bgr(color)
        intensity = min(intensity, 0.8)  # Cap at 80% to keep lip sheen details visible

        h, w = image.shape[:2]
        lip_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(lip_mask, [upper_lip_pts], 255)
        cv2.fillPoly(lip_mask, [lower_lip_pts], 255)

        lip_mask = cv2.GaussianBlur(lip_mask, (3, 3), 0)

        # Normal alpha blend over mask region
        mask_float = lip_mask.astype(np.float32) / 255.0
        mask_3d = np.expand_dims(mask_float * intensity, axis=2)

        lipstick_layer = np.full_like(image, bgr_color, dtype=np.uint8)
        
        output = image.astype(np.float32) * (1.0 - mask_3d) + lipstick_layer.astype(np.float32) * mask_3d
        return np.clip(output, 0, 255).astype(np.uint8)
