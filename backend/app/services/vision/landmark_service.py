from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmark
from app.constants import landmarks as lmark_const


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
        ][:468]

    @staticmethod
    def get_lips(landmarks: list[tuple[float, float]]) -> list[tuple[float, float]]:
        return [landmarks[idx] for idx in lmark_const.LIPS]

    @staticmethod
    def get_left_eye(landmarks: list[tuple[float, float]]) -> list[tuple[float, float]]:
        return [landmarks[idx] for idx in lmark_const.LEFT_EYE]

    @staticmethod
    def get_right_eye(landmarks: list[tuple[float, float]]) -> list[tuple[float, float]]:
        return [landmarks[idx] for idx in lmark_const.RIGHT_EYE]

    @staticmethod
    def get_face_outline(landmarks: list[tuple[float, float]]) -> list[tuple[float, float]]:
        return [landmarks[idx] for idx in lmark_const.FACE_OUTLINE]

    @staticmethod
    def get_left_eyebrow(landmarks: list[tuple[float, float]]) -> list[tuple[float, float]]:
        return [landmarks[idx] for idx in lmark_const.LEFT_EYEBROW]

    @staticmethod
    def get_right_eyebrow(landmarks: list[tuple[float, float]]) -> list[tuple[float, float]]:
        return [landmarks[idx] for idx in lmark_const.RIGHT_EYEBROW]

