from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SavedLookBase(BaseModel):
    name: str
    lipstick_color: Optional[str] = None
    lipstick_opacity: Optional[float] = 0.0
    blush_color: Optional[str] = None
    blush_opacity: Optional[float] = 0.0
    foundation_color: Optional[str] = None
    foundation_opacity: Optional[float] = 0.0
    eyeshadow_color: Optional[str] = None
    eyeshadow_opacity: Optional[float] = 0.0
    eyeliner_color: Optional[str] = None
    eyeliner_opacity: Optional[float] = 0.0
    eyebrow_color: Optional[str] = None
    eyebrow_opacity: Optional[float] = 0.0


class SavedLookCreate(SavedLookBase):
    pass


class SavedLookResponse(SavedLookBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
