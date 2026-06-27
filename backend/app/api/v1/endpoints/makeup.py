import io
import cv2
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse

from app.services.vision.image_service import ImageService
from app.services.vision.image_validator import ImageValidator
from app.services.vision.pipeline import VisionPipeline
from app.services.rendering.rendering_service import RenderingService
from app.constants.presets import PRESETS
from app.schemas.rendering import RenderingOptions

router = APIRouter()
vision_pipeline = VisionPipeline()


@router.post("/render-makeup")
async def render_makeup(
    image: UploadFile = File(...),
    look_preset: str = Form(None),
    lipstick_color: str = Form(None),
    lipstick_opacity: float = Form(0.0),
    blush_color: str = Form(None),
    blush_opacity: float = Form(0.0),
    foundation_color: str = Form(None),
    foundation_opacity: float = Form(0.0),
    eyeshadow_color: str = Form(None),
    eyeshadow_opacity: float = Form(0.0),
    eyeliner_color: str = Form(None),
    eyeliner_opacity: float = Form(0.0),
    eyebrow_color: str = Form(None),
    eyebrow_opacity: float = Form(0.0),
):
    """
    Accepts a selfie image, runs VisionPipeline to get VisionContext, applies the specified
    blush, lipstick, foundation, eyeshadow, eyeliner, and eyebrow filters (either via preset or manually),
    and streams the finished JPEG.
    """
    await ImageValidator.validate(image)

    image_bytes = await image.read()
    img_cv = ImageService.decode(image_bytes)

    # Extract Face Mesh landmarks & metadata in a single pipeline execution
    context = vision_pipeline.process(img_cv)

    # Normalize empty inputs to None
    def normalize_input(val: str) -> str:
        if not val or val.strip() == "":
            return None
        return val

    lipstick_color = normalize_input(lipstick_color)
    blush_color = normalize_input(blush_color)
    foundation_color = normalize_input(foundation_color)
    eyeshadow_color = normalize_input(eyeshadow_color)
    eyeliner_color = normalize_input(eyeliner_color)
    eyebrow_color = normalize_input(eyebrow_color)

    # Resolve presets if look_preset is provided
    base_opts = {}
    if look_preset and look_preset.strip() != "":
        skin_tone = context.skin_tone
        base_opts = PRESETS.get(skin_tone, {}).get(look_preset, {})

    # Collect options (user parameters override preset defaults)
    options = {
        "lipstick_color": lipstick_color if lipstick_color else base_opts.get("lipstick_color"),
        "lipstick_opacity": lipstick_opacity if lipstick_opacity > 0.0 else base_opts.get("lipstick_opacity", 0.0),
        "blush_color": blush_color if blush_color else base_opts.get("blush_color"),
        "blush_opacity": blush_opacity if blush_opacity > 0.0 else base_opts.get("blush_opacity", 0.0),
        "foundation_color": foundation_color if foundation_color else base_opts.get("foundation_color"),
        "foundation_opacity": foundation_opacity if foundation_opacity > 0.0 else base_opts.get("foundation_opacity", 0.0),
        "eyeshadow_color": eyeshadow_color if eyeshadow_color else base_opts.get("eyeshadow_color"),
        "eyeshadow_opacity": eyeshadow_opacity if eyeshadow_opacity > 0.0 else base_opts.get("eyeshadow_opacity", 0.0),
        "eyeliner_color": eyeliner_color if eyeliner_color else base_opts.get("eyeliner_color"),
        "eyeliner_opacity": eyeliner_opacity if eyeliner_opacity > 0.0 else base_opts.get("eyeliner_opacity", 0.0),
        "eyebrow_color": eyebrow_color if eyebrow_color else base_opts.get("eyebrow_color"),
        "eyebrow_opacity": eyebrow_opacity if eyebrow_opacity > 0.0 else base_opts.get("eyebrow_opacity", 0.0),
    }
    # Render filters using rendering service which consumes the context
    try:
        rendering_opts = RenderingOptions(**options)
        rendered_img = RenderingService.render_makeup(context, rendering_opts)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid color parameter format: {str(e)}"
        )

    # Encode to JPEG
    success, encoded_img = cv2.imencode(".jpg", rendered_img)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to encode rendered output image."
        )

    return StreamingResponse(
        io.BytesIO(encoded_img.tobytes()),
        media_type="image/jpeg"
    )
