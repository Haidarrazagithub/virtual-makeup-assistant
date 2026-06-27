import base64
import cv2
import io
import mediapipe as mp
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.product import Product
from app.services.vision.image_validator import ImageValidator
from app.services.vision.image_service import ImageService
from app.services.vision.landmark_service import LandmarkService
from app.services.vision.skin_tone_service import SkinToneService
from app.services.vision.face_shape_service import FaceShapeService
from app.services.vision.makeup_rendering_service import MakeupRenderingService
from app.services.recommendation.recommendation_service import RecommendationService
from app.services.recommendation.genai_service import GenAIService

router = APIRouter()

# Re-use MediaPipe Face Mesh model configuration
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5
)


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


@router.post("/recommend-look")
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
    # 1. Validate image format and dimensions
    await ImageValidator.validate(image)

    # 2. Decode image
    image_bytes = await image.read()
    img_cv = ImageService.decode(image_bytes)

    # 3. Extract Face Mesh landmarks
    rgb_img = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_img)

    if not results.multi_face_landmarks:
        raise HTTPException(
            status_code=400,
            detail="No face detected in the image."
        )

    face_landmarks = results.multi_face_landmarks[0].landmark
    landmarks = LandmarkService.get_all_landmarks(face_landmarks)

    # 4. Perform Skin Tone & Face Shape Classification
    skin_tone = SkinToneService.detect_skin_tone(img_cv, landmarks)
    face_shape = FaceShapeService.detect_face_shape(landmarks)

    # 5. Call GenAI parser to convert user instructions into makeup adjustments
    genai_opts = await GenAIService.translate_prompt(prompt, skin_tone, face_shape)

    # 6. Resolve look preset if returned by LLM
    look_preset = genai_opts.get("look_preset")
    base_opts = {}
    if look_preset:
        from app.constants.presets import PRESETS
        base_opts = PRESETS.get(skin_tone, {}).get(look_preset, {})

    # 7. Compile options (LLM overrides take precedence over preset defaults)
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
        # Choose llm_val if it exists/is valid, else preset_val
        if llm_val is not None and (not isinstance(llm_val, float) or llm_val > 0.0) and (not isinstance(llm_val, str) or llm_val.strip() != ""):
            compiled_options[key] = llm_val
        else:
            compiled_options[key] = preset_val if preset_val is not None else (0.0 if "opacity" in key else None)

    # 8. Render makeup filters onto the image
    try:
        rendered_img = MakeupRenderingService.apply_makeup(img_cv, landmarks, compiled_options)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error applying translated look parameters: {str(e)}"
        )

    # 9. Fetch product recommendations based on skin tone & shape
    recommended_products = RecommendationService.get_recommendations(db, skin_tone, face_shape)

    # 10. Encode rendered output image to base64
    success, encoded_img = cv2.imencode(".jpg", rendered_img)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to encode rendered output image."
        )

    base64_img = base64.b64encode(encoded_img.tobytes()).decode("utf-8")
    rendered_image_uri = f"data:image/jpeg;base64,{base64_img}"

    return {
        "detected_skin_tone": skin_tone,
        "detected_face_shape": face_shape,
        "resolved_preset": look_preset,
        "applied_options": compiled_options,
        "recommended_products": recommended_products,
        "rendered_image": rendered_image_uri
    }
