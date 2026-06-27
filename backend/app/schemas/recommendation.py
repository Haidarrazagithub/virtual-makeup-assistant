from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class ProductRecommendation(BaseModel):
    """
    Schema representing recommended cosmetic products from the database.
    """
    id: int
    brand: str
    name: str
    category: str
    hex_color: str
    finish: str
    suitability: str
    price: float

    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    """
    Unified response format returned by the try-on recommendation engines.
    """
    detected_skin_tone: str
    detected_face_shape: str
    resolved_preset: Optional[str] = None
    applied_options: Dict[str, Any]
    recommended_products: Dict[str, List[ProductRecommendation]]
    rendered_image: Optional[str] = None


class LLMMakeupRecommendation(BaseModel):
    """
    Schema mapping and validating unstructured text responses from GenAI engines
    into strict makeup options.
    """
    look_preset: Optional[str] = None
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
