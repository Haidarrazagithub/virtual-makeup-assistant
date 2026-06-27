import numpy as np
from app.services.rendering.foundation_renderer import FoundationRenderer
from app.services.rendering.lipstick_renderer import LipstickRenderer
from app.services.rendering.blush_renderer import BlushRenderer
from app.services.rendering.eyeshadow_renderer import EyeshadowRenderer
from app.services.rendering.eyeliner_renderer import EyelinerRenderer
from app.services.rendering.eyebrow_renderer import EyebrowRenderer
from app.services.vision.context import VisionContext
from app.schemas.rendering import RenderingOptions


class RenderingService:
    """
    Coordinator class within the rendering domain that sequences visual makeup try-on renderers
    by utilizing the pre-processed visual state stored inside the VisionContext and Pydantic options.
    """

    @classmethod
    def render_makeup(
        cls,
        context: VisionContext,
        options: RenderingOptions
    ) -> np.ndarray:
        """
        Extracts pre-computed face region coordinate polygons from context and applies makeup layers.
        """
        image = context.original_image
        landmarks = context.landmarks
        regions = context.regions

        if not landmarks or len(landmarks) < 468:
            return image.copy()

        h, w = image.shape[:2]
        rendered = image.copy()

        def scale_pts(normalized_pts: list[tuple[float, float]]) -> np.ndarray:
            return np.array([[int(pt[0] * w), int(pt[1] * h)] for pt in normalized_pts], dtype=np.int32)

        # 1. Foundation
        face_outline_pts = scale_pts(regions["face_outline"])
        left_eye_pts = scale_pts(regions["left_eye"])
        right_eye_pts = scale_pts(regions["right_eye"])
        left_eb_pts = scale_pts(regions["left_eyebrow"])
        right_eb_pts = scale_pts(regions["right_eyebrow"])
        lips_pts = scale_pts(regions["lips"])

        rendered = FoundationRenderer().apply(
            rendered, face_outline_pts, left_eye_pts, right_eye_pts,
            left_eb_pts, right_eb_pts, lips_pts,
            options.foundation_color,
            options.foundation_opacity
        )

        # 2. Eyeshadow
        left_eyeshadow_pts = scale_pts(regions["left_eyeshadow"])
        right_eyeshadow_pts = scale_pts(regions["right_eyeshadow"])
        face_height = np.sqrt((landmarks[10][1] - landmarks[152][1])**2) * h

        rendered = EyeshadowRenderer().apply(
            rendered, left_eyeshadow_pts, right_eyeshadow_pts, face_height,
            options.eyeshadow_color,
            options.eyeshadow_opacity
        )

        # 3. Blush
        left_cheek_pts = scale_pts(regions["left_cheek"])
        right_cheek_pts = scale_pts(regions["right_cheek"])

        rendered = BlushRenderer().apply(
            rendered, left_cheek_pts, right_cheek_pts,
            options.blush_color,
            options.blush_opacity
        )

        # 4. Lipstick
        upper_lip_pts = scale_pts(regions["upper_lip"])
        lower_lip_pts = scale_pts(regions["lower_lip"])

        rendered = LipstickRenderer().apply(
            rendered, upper_lip_pts, lower_lip_pts,
            options.lipstick_color,
            options.lipstick_opacity
        )

        # 5. Eyeliner
        left_eyeliner_pts = scale_pts(regions["left_eyeliner"])
        right_eyeliner_pts = scale_pts(regions["right_eyeliner"])

        rendered = EyelinerRenderer().apply(
            rendered, left_eyeliner_pts, right_eyeliner_pts,
            options.eyeliner_color,
            options.eyeliner_opacity
        )

        # 6. Eyebrows
        rendered = EyebrowRenderer().apply(
            rendered, left_eb_pts, right_eb_pts,
            options.eyebrow_color,
            options.eyebrow_opacity
        )

        return rendered
