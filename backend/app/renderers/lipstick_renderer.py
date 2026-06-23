import cv2
import numpy as np

from app.utils.color import (
    hex_to_bgr
)


class LipstickRenderer:

    def apply(
        self,
        image,
        lip_points,
        color="#FF0000",
        intensity=0.4
    ):

        bgr_color = hex_to_bgr(
            color
        )

        lip_mask = np.zeros(
            image.shape[:2],
            dtype=np.uint8
        )

        cv2.fillPoly(
            lip_mask,
            [lip_points],
            255
        )

        lip_mask = cv2.GaussianBlur(
            lip_mask,
            (11, 11),
            0
        )

        lipstick_layer = np.zeros_like(
            image
        )

        lipstick_layer[:] = bgr_color

        mask_float = (
            lip_mask.astype(np.float32)
            / 255.0
        )

        mask_float = (
            mask_float * intensity
        )

        mask_float = np.expand_dims(
            mask_float,
            axis=2
        )

        output = (
            image.astype(np.float32)
            * (1 - mask_float)
            +
            lipstick_layer.astype(np.float32)
            * mask_float
        )

        return output.astype(
            np.uint8
        )
