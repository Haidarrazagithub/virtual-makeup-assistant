import cv2
import numpy as np
from app.utils.color import hex_to_bgr


class EyeshadowRenderer:
    """
    Renders soft eyeshadow overlays projected above left and right eyelids.
    """

    def apply(
        self,
        image: np.ndarray,
        left_eye_contour: np.ndarray,
        right_eye_contour: np.ndarray,
        face_height: float,
        color: str = "#E6E6FA",
        intensity: float = 0.4
    ) -> np.ndarray:
        if not color or intensity <= 0.0:
            return image

        bgr_color = hex_to_bgr(color)
        intensity = min(intensity, 0.5)  # Cap at 50% for soft blend

        h, w = image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)

        # Upper eyelid indices are ordered in the input arrays
        for eye_pts in [left_eye_contour, right_eye_contour]:
            # Project upper eyelid points upwards based on face height factor (3.5%)
            projected_pts = np.array([
                [pt[0], int(pt[1] - face_height * 0.035)]
                for pt in eye_pts
            ], dtype=np.int32)

            # Form a closed loop polygon
            poly_pts = np.concatenate((eye_pts, projected_pts[::-1]), axis=0)
            cv2.fillPoly(mask, [poly_pts], 255)

        mask = cv2.GaussianBlur(mask, (11, 11), 0)

        # Blend
        mask_float = mask.astype(np.float32) / 255.0
        mask_3d = np.expand_dims(mask_float * intensity, axis=2)

        eyeshadow_layer = np.full_like(image, bgr_color, dtype=np.uint8)
        output = image.astype(np.float32) * (1.0 - mask_3d) + eyeshadow_layer.astype(np.float32) * mask_3d
        return np.clip(output, 0, 255).astype(np.uint8)
