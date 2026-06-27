import cv2
import numpy as np
from app.constants import landmarks as lmark_const


class SkinToneService:
    """
    Service for determining the skin tone of a face
    using the HSV color space of the cheek regions.
    """

    @staticmethod
    def detect_skin_tone(image: np.ndarray, landmarks: list[tuple[float, float]]) -> str:
        """
        Determines the skin tone (Warm, Cool, or Neutral) based on cheek regions.
        """
        if not landmarks or len(landmarks) < 300:
            return "Neutral"

        h_img, w_img = image.shape[:2]
        if h_img == 0 or w_img == 0:
            return "Neutral"

        # Extract coordinates for left and right cheek
        try:
            left_cheek_pts = np.array([
                [int(landmarks[idx][0] * w_img), int(landmarks[idx][1] * h_img)]
                for idx in lmark_const.LEFT_CHEEK
            ], dtype=np.int32)

            right_cheek_pts = np.array([
                [int(landmarks[idx][0] * w_img), int(landmarks[idx][1] * h_img)]
                for idx in lmark_const.RIGHT_CHEEK
            ], dtype=np.int32)
        except IndexError:
            return "Neutral"

        # Create a mask for the cheeks
        mask = np.zeros((h_img, w_img), dtype=np.uint8)
        cv2.fillPoly(mask, [left_cheek_pts], 255)
        cv2.fillPoly(mask, [right_cheek_pts], 255)

        # Check if the mask has any non-zero pixels
        if cv2.countNonZero(mask) == 0:
            return "Neutral"

        # Compute average color in BGR (since image is BGR)
        mean_bgr = cv2.mean(image, mask=mask)[:3]

        # Convert BGR to RGB
        mean_rgb = (mean_bgr[2], mean_bgr[1], mean_bgr[0])

        # Convert RGB to HSV
        rgb_pixel = np.uint8([[mean_rgb]])
        hsv_pixel = cv2.cvtColor(rgb_pixel, cv2.COLOR_RGB2HSV)[0][0]

        # Hue is scaled 0-179 in OpenCV, so multiply by 2 to get 0-360 range
        hue = hsv_pixel[0] * 2

        # Apply classification heuristics
        if hue < 20:
            return "Cool"
        elif 20 <= hue <= 28:
            return "Neutral"
        else:
            return "Warm"
