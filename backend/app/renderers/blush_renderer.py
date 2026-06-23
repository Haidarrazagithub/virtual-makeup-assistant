import cv2
import numpy as np

from app.utils.color import (
    hex_to_bgr
)


class BlushRenderer:

    def apply(
        self,
        image,
        left_cheek,
        right_cheek,
        color="#FFB6C1",
        intensity=0.15
    ):

        blush_color = hex_to_bgr(
            color
        )

        left_center = tuple(
            left_cheek.mean(
                axis=0
            ).astype(int)
        )

        right_center = tuple(
            right_cheek.mean(
                axis=0
            ).astype(int)
        )

        mask = np.zeros_like(
            image
        )

        cv2.circle(
            mask,
            left_center,
            35,
            blush_color,
            -1
        )

        cv2.circle(
            mask,
            right_center,
            35,
            blush_color,
            -1
        )

        mask = cv2.GaussianBlur(
            mask,
            (51, 51),
            0
        )

        output = cv2.addWeighted(
            image,
            1 - intensity,
            mask,
            intensity,
            0
        )

        return output
