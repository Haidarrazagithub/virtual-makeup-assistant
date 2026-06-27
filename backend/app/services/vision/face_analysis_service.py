import numpy as np
from app.schemas.face_analysis import FaceAnalysisResponse
from app.services.vision.pipeline import VisionPipeline
from app.constants.presets import PRESETS


from app.services.vision.context import VisionContext


class FaceAnalysisService:
    """
    Service wrapper that handles endpoints face analysis.
    Delegates vision processing actions directly to the VisionPipeline.
    """

    def __init__(self) -> None:
        self.pipeline = VisionPipeline()

    def analyze(
        self,
        context: VisionContext,
    ) -> FaceAnalysisResponse:
        """
        Executes pipeline processing and constructs the FaceAnalysisResponse format.
        """
        # Fetch matching preset styles
        recommended = PRESETS.get(context.skin_tone)

        return FaceAnalysisResponse(
            face_detected=True,
            face_count=context.face_count,
            landmark_count=len(context.landmarks),
            skin_tone=context.skin_tone,
            face_shape=context.face_shape,
            recommended_presets=recommended
        )
