from fastapi import HTTPException

from app.services.face_landmark_service import (
    FaceLandmarkService
)

from app.renderers.lipstick_renderer import (
    LipstickRenderer
)

from app.renderers.blush_renderer import (
    BlushRenderer
)


class MakeupLookService:

    LOOKS = {

        "office": {
            "lipstick_color": "#C68642",
            "lipstick_intensity": 0.25,
            "blush_color": "#FFB6C1",
            "blush_intensity": 0.10,
        },

        "party": {
            "lipstick_color": "#FF0000",
            "lipstick_intensity": 0.60,
            "blush_color": "#FF69B4",
            "blush_intensity": 0.20,
        },

        "bridal": {
            "lipstick_color": "#8B0000",
            "lipstick_intensity": 0.75,
            "blush_color": "#FF1493",
            "blush_intensity": 0.30,
        }
    }

    async def apply_look(
        self,
        image_file,
        look: str
    ):

        if look not in self.LOOKS:
            raise HTTPException(
                status_code=400,
                detail=f"Look '{look}' not supported"
            )

        config = self.LOOKS[look]

        landmark_service = (
            FaceLandmarkService()
        )

        data = await landmark_service.get_landmarks(
            image_file
        )

        image = data["image"]

        image = LipstickRenderer().apply(
            image=image,
            lip_points=data["lip_points"],
            color=config["lipstick_color"],
            intensity=config["lipstick_intensity"]
        )

        image = BlushRenderer().apply(
            image=image,
            left_cheek=data["left_cheek_points"],
            right_cheek=data["right_cheek_points"],
            color=config["blush_color"],
            intensity=config["blush_intensity"]
        )

        return image
