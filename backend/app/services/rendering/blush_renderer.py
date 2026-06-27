import cv2
import numpy as np
from app.utils.color import hex_to_bgr


class BlushRenderer:
    """
    Renders soft blush circles over left and right cheek coordinates.
    """

    def apply(
        self,
        image: np.ndarray,
        left_cheek: np.ndarray,
        right_cheek: np.ndarray,
        color: str = "#FFB6C1",
        intensity: float = 0.15
    ) -> np.ndarray:
        if not color or intensity <= 0.0:
            return image

        blush_color = hex_to_bgr(color)
        intensity = min(intensity, 0.4)  # Cap at 40% for natural flushing

        left_mean = left_cheek.mean(axis=0)
        right_mean = right_cheek.mean(axis=0)
        
        # Calculate cheeks distance using NumPy arrays
        cheeks_dist = np.linalg.norm(left_mean - right_mean)
        radius = int(cheeks_dist * 0.15)  # Tighten cheeks radius

        left_center = tuple(left_mean.astype(int))
        right_center = tuple(right_mean.astype(int))

        h, w = image.shape[:2]
        blush_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(blush_mask, left_center, radius, 255, -1)
        cv2.circle(blush_mask, right_center, radius, 255, -1)

        blush_mask = cv2.GaussianBlur(blush_mask, (35, 35), 0)

        # Blend only on mask region (prevents darkening the rest of the image)
        mask_float = blush_mask.astype(np.float32) / 255.0
        mask_3d = np.expand_dims(mask_float * intensity, axis=2)

        blush_layer = np.full_like(image, blush_color, dtype=np.uint8)
        output = image.astype(np.float32) * (1.0 - mask_3d) + blush_layer.astype(np.float32) * mask_3d
        return np.clip(output, 0, 255).astype(np.uint8)
