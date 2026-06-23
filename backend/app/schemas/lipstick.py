from pydantic import BaseModel


class LipstickResponse(
    BaseModel
):
    message: str
    lip_points_count: int
