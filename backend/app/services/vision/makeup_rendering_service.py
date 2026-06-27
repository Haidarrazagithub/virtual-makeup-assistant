import cv2
import numpy as np
from app.constants import landmarks as lmark_const


class MakeupRenderingService:
    """
    Applies virtual makeup filters (lipstick, blush, foundation, eyeshadow)
    to a facial image based on landmarks.
    """

    @staticmethod
    def hex_to_bgr(hex_color: str) -> tuple[int, int, int]:
        """
        Converts hex color string (e.g., "#FF0000") to BGR tuple.
        """
        if not hex_color:
            return (0, 0, 0)
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError("Hex color must be exactly 6 characters long (excluding #).")
        
        # Validate that all characters are hex digits
        if not all(c in "0123456789abcdefABCDEF" for c in hex_color):
            raise ValueError(f"Invalid hex color '{hex_color}'. Hex color must contain only valid hexadecimal characters.")
            
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (b, g, r)

    @classmethod
    def apply_makeup(
        cls,
        image: np.ndarray,
        landmarks: list[tuple[float, float]],
        options: dict
    ) -> np.ndarray:
        """
        Applies requested makeup effects sequentially.
        """
        if not landmarks or len(landmarks) < 468:
            return image.copy()

        rendered = image.copy()

        # 1. Foundation
        foundation_color_hex = options.get("foundation_color")
        foundation_opacity = options.get("foundation_opacity", 0.0)
        if foundation_color_hex and foundation_opacity > 0:
            color_bgr = cls.hex_to_bgr(foundation_color_hex)
            rendered = cls._apply_foundation(rendered, landmarks, color_bgr, foundation_opacity)

        # 2. Eyeshadow
        eyeshadow_color_hex = options.get("eyeshadow_color")
        eyeshadow_opacity = options.get("eyeshadow_opacity", 0.0)
        if eyeshadow_color_hex and eyeshadow_opacity > 0:
            color_bgr = cls.hex_to_bgr(eyeshadow_color_hex)
            rendered = cls._apply_eyeshadow(rendered, landmarks, color_bgr, eyeshadow_opacity)

        # 3. Blush
        blush_color_hex = options.get("blush_color")
        blush_opacity = options.get("blush_opacity", 0.0)
        if blush_color_hex and blush_opacity > 0:
            color_bgr = cls.hex_to_bgr(blush_color_hex)
            rendered = cls._apply_blush(rendered, landmarks, color_bgr, blush_opacity)

        # 4. Lipstick
        lipstick_color_hex = options.get("lipstick_color")
        lipstick_opacity = options.get("lipstick_opacity", 0.0)
        if lipstick_color_hex and lipstick_opacity > 0:
            color_bgr = cls.hex_to_bgr(lipstick_color_hex)
            rendered = cls._apply_lipstick(rendered, landmarks, color_bgr, lipstick_opacity)

        # 5. Eyeliner
        eyeliner_color_hex = options.get("eyeliner_color")
        eyeliner_opacity = options.get("eyeliner_opacity", 0.0)
        if eyeliner_color_hex and eyeliner_opacity > 0:
            color_bgr = cls.hex_to_bgr(eyeliner_color_hex)
            rendered = cls._apply_eyeliner(rendered, landmarks, color_bgr, eyeliner_opacity)

        # 6. Eyebrows
        eyebrow_color_hex = options.get("eyebrow_color")
        eyebrow_opacity = options.get("eyebrow_opacity", 0.0)
        if eyebrow_color_hex and eyebrow_opacity > 0:
            color_bgr = cls.hex_to_bgr(eyebrow_color_hex)
            rendered = cls._apply_eyebrows(rendered, landmarks, color_bgr, eyebrow_opacity)

        return rendered

    @staticmethod
    def _blend_color_with_mask(
        image: np.ndarray,
        mask: np.ndarray,
        color_bgr: tuple[int, int, int],
        opacity: float
    ) -> np.ndarray:
        """
        Blends a BGR color onto an image based on a single-channel feathered mask and opacity.
        """
        mask_float = mask.astype(float) / 255.0
        mask_3d = np.expand_dims(mask_float, axis=2)
        color_img = np.full_like(image, color_bgr, dtype=np.uint8)

        # Cast to float to prevent integer overflow/underflow in uint8 math
        image_float = image.astype(float)
        color_float = color_img.astype(float)

        # Formula: Image * (1 - Mask * Opacity) + Color * (Mask * Opacity)
        blended = image_float * (1.0 - mask_3d * opacity) + color_float * (mask_3d * opacity)
        return blended.astype(np.uint8)

    @classmethod
    def _apply_lipstick(
        cls,
        image: np.ndarray,
        landmarks: list[tuple[float, float]],
        color_bgr: tuple[int, int, int],
        opacity: float
    ) -> np.ndarray:
        h, w = image.shape[:2]

        # Extract coordinates
        upper_pts = np.array([
            [int(landmarks[idx][0] * w), int(landmarks[idx][1] * h)]
            for idx in lmark_const.UPPER_LIP
        ], dtype=np.int32)

        lower_pts = np.array([
            [int(landmarks[idx][0] * w), int(landmarks[idx][1] * h)]
            for idx in lmark_const.LOWER_LIP
        ], dtype=np.int32)

        # Create mask
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [upper_pts], 255)
        cv2.fillPoly(mask, [lower_pts], 255)

        # Apply feathering
        mask = cv2.GaussianBlur(mask, (7, 7), 0)

        return cls._blend_color_with_mask(image, mask, color_bgr, opacity)

    @classmethod
    def _apply_blush(
        cls,
        image: np.ndarray,
        landmarks: list[tuple[float, float]],
        color_bgr: tuple[int, int, int],
        opacity: float
    ) -> np.ndarray:
        h, w = image.shape[:2]

        left_pts = np.array([
            [int(landmarks[idx][0] * w), int(landmarks[idx][1] * h)]
            for idx in lmark_const.LEFT_CHEEK
        ], dtype=np.int32)

        right_pts = np.array([
            [int(landmarks[idx][0] * w), int(landmarks[idx][1] * h)]
            for idx in lmark_const.RIGHT_CHEEK
        ], dtype=np.int32)

        # Calculate centers
        left_center = np.mean(left_pts, axis=0).astype(int)
        right_center = np.mean(right_pts, axis=0).astype(int)

        # Base radius on face width (distance between 234 and 454)
        p234 = landmarks[234]
        p454 = landmarks[454]
        face_width = np.sqrt((p234[0] - p454[0])**2 + (p234[1] - p454[1])**2) * w
        radius = int(face_width * 0.12)  # 12% of face width

        # Create mask
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask, tuple(left_center), radius, 255, -1)
        cv2.circle(mask, tuple(right_center), radius, 255, -1)

        # Heavy blur for smooth blend
        mask = cv2.GaussianBlur(mask, (55, 55), 0)

        return cls._blend_color_with_mask(image, mask, color_bgr, opacity)

    @classmethod
    def _apply_foundation(
        cls,
        image: np.ndarray,
        landmarks: list[tuple[float, float]],
        color_bgr: tuple[int, int, int],
        opacity: float
    ) -> np.ndarray:
        h, w = image.shape[:2]

        face_pts = np.array([
            [int(landmarks[idx][0] * w), int(landmarks[idx][1] * h)]
            for idx in lmark_const.FACE_OUTLINE
        ], dtype=np.int32)

        left_eye_pts = np.array([
            [int(landmarks[idx][0] * w), int(landmarks[idx][1] * h)]
            for idx in lmark_const.LEFT_EYE
        ], dtype=np.int32)

        right_eye_pts = np.array([
            [int(landmarks[idx][0] * w), int(landmarks[idx][1] * h)]
            for idx in lmark_const.RIGHT_EYE
        ], dtype=np.int32)

        left_eb_pts = np.array([
            [int(landmarks[idx][0] * w), int(landmarks[idx][1] * h)]
            for idx in lmark_const.LEFT_EYEBROW
        ], dtype=np.int32)

        right_eb_pts = np.array([
            [int(landmarks[idx][0] * w), int(landmarks[idx][1] * h)]
            for idx in lmark_const.RIGHT_EYEBROW
        ], dtype=np.int32)

        lips_pts = np.array([
            [int(landmarks[idx][0] * w), int(landmarks[idx][1] * h)]
            for idx in lmark_const.LIPS
        ], dtype=np.int32)

        # Create base skin mask
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [face_pts], 255)

        # Exclude details (fill with 0)
        cv2.fillPoly(mask, [left_eye_pts], 0)
        cv2.fillPoly(mask, [right_eye_pts], 0)
        cv2.fillPoly(mask, [left_eb_pts], 0)
        cv2.fillPoly(mask, [right_eb_pts], 0)
        cv2.fillPoly(mask, [lips_pts], 0)

        # Smooth edges
        mask = cv2.GaussianBlur(mask, (21, 21), 0)

        return cls._blend_color_with_mask(image, mask, color_bgr, opacity)

    @classmethod
    def _apply_eyeshadow(
        cls,
        image: np.ndarray,
        landmarks: list[tuple[float, float]],
        color_bgr: tuple[int, int, int],
        opacity: float
    ) -> np.ndarray:
        h, w = image.shape[:2]

        # Get face height to scale the eyeshadow projection
        p10 = landmarks[10]
        p152 = landmarks[152]
        face_height = np.sqrt((p10[0] - p152[0])**2 + (p10[1] - p152[1])**2) * h

        mask = np.zeros((h, w), dtype=np.uint8)

        # Eyeshadow region for each eye: project upper eye contour upwards
        left_eye_indices = [33, 160, 159, 158, 157, 173, 133]
        right_eye_indices = [263, 387, 386, 385, 384, 398, 362]

        for eye_indices in [left_eye_indices, right_eye_indices]:
            eye_pts = [
                (int(landmarks[idx][0] * w), int(landmarks[idx][1] * h))
                for idx in eye_indices
            ]

            # Project upper eyelid points upwards (subtract Y coordinate)
            # Projection factor: 4.5% of face height
            projected_pts = [
                (pt[0], int(pt[1] - face_height * 0.045))
                for pt in eye_pts
            ]

            # Form a closed polygon: eye contour going forward, projected contour going in reverse
            poly_pts = np.array(eye_pts + projected_pts[::-1], dtype=np.int32)
            cv2.fillPoly(mask, [poly_pts], 255)

        # Blur eyeshadow mask heavily
        mask = cv2.GaussianBlur(mask, (21, 21), 0)

        return cls._blend_color_with_mask(image, mask, color_bgr, opacity)

    @classmethod
    def _apply_eyeliner(
        cls,
        image: np.ndarray,
        landmarks: list[tuple[float, float]],
        color_bgr: tuple[int, int, int],
        opacity: float
    ) -> np.ndarray:
        h, w = image.shape[:2]

        left_eye_indices = [33, 160, 159, 158, 157, 173, 133]
        right_eye_indices = [263, 387, 386, 385, 384, 398, 362]

        mask = np.zeros((h, w), dtype=np.uint8)

        for eye_indices in [left_eye_indices, right_eye_indices]:
            pts = np.array([
                [int(landmarks[idx][0] * w), int(landmarks[idx][1] * h)]
                for idx in eye_indices
            ], dtype=np.int32)
            cv2.polylines(mask, [pts], isClosed=False, color=255, thickness=2)

        # Soften eyeliner line edge slightly
        mask = cv2.GaussianBlur(mask, (3, 3), 0)

        return cls._blend_color_with_mask(image, mask, color_bgr, opacity)

    @classmethod
    def _apply_eyebrows(
        cls,
        image: np.ndarray,
        landmarks: list[tuple[float, float]],
        color_bgr: tuple[int, int, int],
        opacity: float
    ) -> np.ndarray:
        h, w = image.shape[:2]

        left_eb_pts = np.array([
            [int(landmarks[idx][0] * w), int(landmarks[idx][1] * h)]
            for idx in lmark_const.LEFT_EYEBROW
        ], dtype=np.int32)

        right_eb_pts = np.array([
            [int(landmarks[idx][0] * w), int(landmarks[idx][1] * h)]
            for idx in lmark_const.RIGHT_EYEBROW
        ], dtype=np.int32)

        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [left_eb_pts], 255)
        cv2.fillPoly(mask, [right_eb_pts], 255)

        # Soften eyebrows
        mask = cv2.GaussianBlur(mask, (9, 9), 0)

        return cls._blend_color_with_mask(image, mask, color_bgr, opacity)
