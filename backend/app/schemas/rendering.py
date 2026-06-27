from pydantic import BaseModel, Field
from typing import Optional

class RenderingOptions(BaseModel):
    """
    Pydantic schema representing type-safe makeup rendering parameters.
    """
    lipstick_color: Optional[str] = Field(default=None, description="Hex color for lipstick")
    lipstick_opacity: float = Field(default=0.0, description="Opacity of lipstick from 0.0 to 1.0")
    
    blush_color: Optional[str] = Field(default=None, description="Hex color for blush")
    blush_opacity: float = Field(default=0.0, description="Opacity of blush from 0.0 to 1.0")
    
    foundation_color: Optional[str] = Field(default=None, description="Hex color for foundation")
    foundation_opacity: float = Field(default=0.0, description="Opacity of foundation from 0.0 to 1.0")
    
    eyeshadow_color: Optional[str] = Field(default=None, description="Hex color for eyeshadow")
    eyeshadow_opacity: float = Field(default=0.0, description="Opacity of eyeshadow from 0.0 to 1.0")
    
    eyeliner_color: Optional[str] = Field(default=None, description="Hex color for eyeliner")
    eyeliner_opacity: float = Field(default=0.0, description="Opacity of eyeliner from 0.0 to 1.0")
    
    eyebrow_color: Optional[str] = Field(default=None, description="Hex color for eyebrow shadow")
    eyebrow_opacity: float = Field(default=0.0, description="Opacity of eyebrow from 0.0 to 1.0")
