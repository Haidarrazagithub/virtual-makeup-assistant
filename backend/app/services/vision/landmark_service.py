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

    @staticmethod
    def get_regions(landmarks: list[tuple[float, float]]) -> dict[str, list[tuple[float, float]]]:
        """
        Groups all facial landmark coordinates into logical named regions.
        """
        return {
            "face_outline": [landmarks[idx] for idx in lmark_const.FACE_OUTLINE],
            "left_eye": [landmarks[idx] for idx in lmark_const.LEFT_EYE],
            "right_eye": [landmarks[idx] for idx in lmark_const.RIGHT_EYE],
            "left_eyebrow": [landmarks[idx] for idx in lmark_const.LEFT_EYEBROW],
            "right_eyebrow": [landmarks[idx] for idx in lmark_const.RIGHT_EYEBROW],
            "lips": [landmarks[idx] for idx in lmark_const.LIPS],
            "upper_lip": [landmarks[idx] for idx in lmark_const.UPPER_LIP],
            "lower_lip": [landmarks[idx] for idx in lmark_const.LOWER_LIP],
            "left_cheek": [landmarks[idx] for idx in lmark_const.LEFT_CHEEK],
            "right_cheek": [landmarks[idx] for idx in lmark_const.RIGHT_CHEEK],
            "left_eyeliner": [landmarks[idx] for idx in [33, 160, 159, 158, 157, 173, 133]],
            "right_eyeliner": [landmarks[idx] for idx in [263, 387, 386, 385, 384, 398, 362]],
            "left_eyeshadow": [landmarks[idx] for idx in [33, 160, 159, 158, 157, 173, 133]],
            "right_eyeshadow": [landmarks[idx] for idx in [263, 387, 386, 385, 384, 398, 362]],
        }

