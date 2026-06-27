import base64
import cv2
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.product import Product
from app.schemas.recommendation import RecommendationResponse
from app.services.vision.image_validator import ImageValidator
from app.services.vision.image_service import ImageService
from app.services.vision.pipeline import VisionPipeline
from app.services.rendering.rendering_service import RenderingService
from app.services.catalog.catalog_service import CatalogService
from app.services.assistant.genai_service import GenAIService
from app.schemas.rendering import RenderingOptions

router = APIRouter()
pipeline = VisionPipeline()


@router.get("/products")
def list_products(
    category: Optional[str] = None,
    suitability: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieves all cosmetic products from the catalog database.
    Allows optional filtering by category or skin suitability.
    """
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if suitability:
        query = query.filter(Product.suitability == suitability)
    
    products = query.all()
    return [
        {
            "id": p.id,
            "brand": p.brand,
            "name": p.name,
            "category": p.category,
            "hex_color": p.hex_color,
            "finish": p.finish,
            "suitability": p.suitability,
            "price": p.price
        }
        for p in products
    ]


@router.post("/recommend-look", response_model=RecommendationResponse)
async def recommend_look(
    image: UploadFile = File(...),
    prompt: str = Form("Give me natural office makeup"),
    db: Session = Depends(get_db)
):
    """
    Combines skin tone and face shape detection with conversational prompt understanding.
    Translates user requests into recommended looks, seeds product catalog matches,
    renders the look onto the face, and returns the finished image as a base64 string
    along with product models.
    """
    await ImageValidator.validate(image)

    image_bytes = await image.read()
    img_cv = ImageService.decode(image_bytes)

    # Process image once through the pipeline to obtain the VisionContext
    context = pipeline.process(img_cv)

    # Call GenAI parser using the unified context
    genai_opts = await GenAIService.translate_prompt(prompt, context)

    look_preset = genai_opts.get("look_preset")
    base_opts = {}
    if look_preset:
        from app.constants.presets import PRESETS
        base_opts = PRESETS.get(context.skin_tone, {}).get(look_preset, {})

    # Compile options (LLM overrides take precedence over preset defaults)
    compiled_options = {}
    keys = [
        "lipstick_color", "lipstick_opacity",
        "blush_color", "blush_opacity",
        "foundation_color", "foundation_opacity",
        "eyeshadow_color", "eyeshadow_opacity",
        "eyeliner_color", "eyeliner_opacity",
        "eyebrow_color", "eyebrow_opacity"
    ]
    for key in keys:
        llm_val = genai_opts.get(key)
        preset_val = base_opts.get(key)
        if llm_val is not None and (not isinstance(llm_val, float) or llm_val > 0.0) and (not isinstance(llm_val, str) or llm_val.strip() != ""):
            compiled_options[key] = llm_val
        else:
            compiled_options[key] = preset_val if preset_val is not None else (0.0 if "opacity" in key else None)

    # Render makeup filters using RenderingService
    try:
        rendering_opts = RenderingOptions(**compiled_options)
        rendered_img = RenderingService.render_makeup(context, rendering_opts)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error applying translated look parameters: {str(e)}"
        )

    # Fetch product recommendations using CatalogService and the context
    recommended_products = CatalogService.get_recommendations(db, context)

    # Encode rendered output image to base64
    success, encoded_img = cv2.imencode(".jpg", rendered_img)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to encode rendered output image."
        )

    base64_img = base64.b64encode(encoded_img.tobytes()).decode("utf-8")
    rendered_image_uri = f"data:image/jpeg;base64,{base64_img}"

    return {
        "detected_skin_tone": context.skin_tone,
        "detected_face_shape": context.face_shape,
        "resolved_preset": look_preset,
        "applied_options": compiled_options,
        "recommended_products": recommended_products,
        "rendered_image": rendered_image_uri
    }
