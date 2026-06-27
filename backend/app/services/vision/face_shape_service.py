import numpy as np


class FaceShapeService:
    """
    Service to classify face shapes based on geometric ratios
    calculated from MediaPipe Face Mesh landmarks.
    """

    @staticmethod
    def detect_face_shape(landmarks: list[tuple[float, float]]) -> str:
        """
        Classifies the face shape as Oval, Round, Square, Heart, Diamond, or Long
        based on ratios of forehead, cheekbones, jaw, and face height.
        """
        if not landmarks or len(landmarks) < 468:
            return "Oval"

        try:
            # Extract coordinates for required landmarks
            p10 = landmarks[10]    # Forehead top
            p152 = landmarks[152]  # Chin
            p234 = landmarks[234]  # Left cheekbone outer
            p454 = landmarks[454]  # Right cheekbone outer
            p103 = landmarks[103]  # Left forehead outer
            p332 = landmarks[332]  # Right forehead outer
            p136 = landmarks[136]  # Left jaw corner
            p365 = landmarks[365]  # Right jaw corner

            # Helper function for 2D Euclidean distance
            def dist(pt1: tuple[float, float], pt2: tuple[float, float]) -> float:
                return float(np.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2))

            # Compute key dimensions
            height = dist(p10, p152)
            w_cheek = dist(p234, p454)
            w_forehead = dist(p103, p332)
            w_jaw = dist(p136, p365)

            if w_cheek == 0 or w_forehead == 0 or w_jaw == 0:
                return "Oval"

            # Calculate proportion ratios
            aspect_ratio = height / w_cheek
            forehead_cheek_ratio = w_forehead / w_cheek
            jaw_cheek_ratio = w_jaw / w_cheek

            # Classification heuristic logic
            # 1. Long Face: Height is significantly greater than width
            if aspect_ratio > 1.35:
                return "Long"

            # 2. Heart Face: Forehead is wide, face tapers down to narrow jaw/chin
            elif forehead_cheek_ratio > 0.95 and jaw_cheek_ratio < 0.85:
                return "Heart"

            # 3. Diamond Face: Cheekbones are widest, forehead and jaw are narrow
            elif forehead_cheek_ratio < 0.90 and jaw_cheek_ratio < 0.80:
                return "Diamond"

            # 4. Square Face: Similar height/width, wide forehead, wide angular jaw
            elif aspect_ratio <= 1.35 and jaw_cheek_ratio > 0.85 and forehead_cheek_ratio > 0.90:
                return "Square"

            # 5. Round Face: Similar height/width, softer jawline, slightly narrower than cheeks
            elif aspect_ratio <= 1.30 and 0.75 < jaw_cheek_ratio <= 0.85:
                return "Round"

            # 6. Oval Face: Default balanced face
            else:
                return "Oval"

        except (IndexError, TypeError, ZeroDivisionError):
            return "Oval"
