from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmark


class LandmarkService:
    """
    Helper methods for extracting facial regions
    from MediaPipe Face Mesh landmarks.
    """

    @staticmethod
    def get_all_landmarks(landmarks: list[NormalizedLandmark]) -> list[tuple[float, float]]:
        return [
            (point.x, point.y)
            for point in landmarks
        ]
