import cv2
import numpy as np
from app.utils.color import hex_to_bgr


class FoundationRenderer:
    """
    Applies bilateral skin smoothing and subtle skin color correction.
    """

    def apply(
        self,
        image: np.ndarray,
        face_outline: np.ndarray,
        left_eye: np.ndarray,
        right_eye: np.ndarray,
        left_eyebrow: np.ndarray,
        right_eyebrow: np.ndarray,
        lips: np.ndarray,
        color: str = "#F3D2C1",
        intensity: float = 0.3
    ) -> np.ndarray:
        if not color or intensity <= 0.0:
            return image

        bgr_color = hex_to_bgr(color)
        intensity = min(intensity, 0.3)  # Cap at 30% max to preserve real skin textures

        h, w = image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        
        # Draw face polygon and exclude features
        cv2.fillPoly(mask, [face_outline], 255)
        cv2.fillPoly(mask, [left_eye], 0)
        cv2.fillPoly(mask, [right_eye], 0)
        cv2.fillPoly(mask, [left_eyebrow], 0)
        cv2.fillPoly(mask, [right_eyebrow], 0)
        cv2.fillPoly(mask, [lips], 0)

        # Erode mask inward to prevent foundation bleeding into hair/background
        kernel = np.ones((9, 9), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=2)

        mask = cv2.GaussianBlur(mask, (15, 15), 0)

        # 1. Bilateral Skin Smoothing
        smoothed = cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)

        # 2. Color Correction Layer
        mask_3d = np.expand_dims(mask.astype(float) / 255.0, axis=2)
        color_img = np.full_like(image, bgr_color, dtype=np.uint8)
        
        # Max color tint is capped to 15% weight
        tint_factor = 0.15
        blended_skin = smoothed.astype(float) * (1.0 - tint_factor) + color_img.astype(float) * tint_factor
        blended_skin = np.clip(blended_skin, 0, 255).astype(np.uint8)

        # 3. Blend original image with smoothed skin
        image_float = image.astype(float)
        skin_float = blended_skin.astype(float)
        
        final_blended = image_float * (1.0 - mask_3d * intensity) + skin_float * (mask_3d * intensity)
        return np.clip(final_blended, 0, 255).astype(np.uint8)
