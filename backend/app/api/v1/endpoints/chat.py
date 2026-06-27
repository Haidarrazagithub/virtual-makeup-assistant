import uuid
import json
import base64
import cv2
from typing import Optional, List
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import (
    ChatSessionResponse, 
    ChatSessionCreate, 
    ChatMessageResponse
)
from app.services.vision.image_validator import ImageValidator
from app.services.vision.image_service import ImageService
from app.services.vision.pipeline import VisionPipeline
from app.services.vision.context import VisionContext
from app.services.rendering.rendering_service import RenderingService
from app.services.catalog.catalog_service import CatalogService
from app.services.assistant.genai_service import GenAIService
from app.schemas.rendering import RenderingOptions

router = APIRouter()
pipeline = VisionPipeline()


@router.post("/sessions", response_model=ChatSessionResponse)
def create_session(session_in: ChatSessionCreate, db: Session = Depends(get_db)):
    """
    Initializes a new personalization and chat session.
    """
    session_id = session_in.id or str(uuid.uuid4())
    
    db_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not db_session:
        db_session = ChatSession(
            id=session_id,
            skin_tone=session_in.skin_tone,
            face_shape=session_in.face_shape
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
    else:
        if session_in.skin_tone:
            db_session.skin_tone = session_in.skin_tone
        if session_in.face_shape:
            db_session.face_shape = session_in.face_shape
        db.commit()
        db.refresh(db_session)
        
    return db_session


@router.get("/sessions/{session_id}/chat", response_model=List[ChatMessageResponse])
def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """
    Loads all previous dialogue messages for a session.
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        session = ChatSession(id=session_id)
        db.add(session)
        db.commit()
        db.refresh(session)
        
    return db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()


@router.post("/sessions/{session_id}/prompt")
async def process_chat_prompt(
    session_id: str,
    prompt: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Saves the user prompt, reads the last 6 messages for context memory,
    queries the assistant LLM, saves the resolved makeup values, and renders
    the options if an image is provided.
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        session = ChatSession(id=session_id)
        db.add(session)
        db.commit()
        db.refresh(session)

    # Decode and analyze image if uploaded, else load partial context from database session
    if image:
        await ImageValidator.validate(image)
        image_bytes = await image.read()
        img_cv = ImageService.decode(image_bytes)
        
        context = pipeline.process(img_cv)
        
        session.skin_tone = context.skin_tone
        session.face_shape = context.face_shape
        db.commit()
    else:
        context = VisionContext(
            original_image=None,
            rgb_image=None,
            landmarks=[],
            regions={},
            skin_tone=session.skin_tone or "Neutral",
            face_shape=session.face_shape or "Oval",
            face_count=0
        )

    # Read previous 6 messages for conversational context
    history_msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(6)
        .all()
    )
    history_msgs.reverse()

    # Save User prompt to database
    user_msg = ChatMessage(
        session_id=session_id,
        sender="user",
        text=prompt
    )
    db.add(user_msg)
    db.commit()

    # Query LLM with history context and VisionContext
    genai_opts = await GenAIService.translate_prompt(prompt, context, history_msgs)

    # Compile makeup options (presets + overrides)
    look_preset = genai_opts.get("look_preset")
    base_opts = {}
    if look_preset:
        from app.constants.presets import PRESETS
        base_opts = PRESETS.get(context.skin_tone, {}).get(look_preset, {})

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

    # Render makeup overlay if image is loaded
    rendered_image_uri = None
    if context.original_image is not None and len(context.landmarks) > 0:
        try:
            rendering_opts = RenderingOptions(**compiled_options)
            rendered_img = RenderingService.render_makeup(context, rendering_opts)
            success, encoded_img = cv2.imencode(".jpg", rendered_img)
            if success:
                base64_img = base64.b64encode(encoded_img.tobytes()).decode("utf-8")
                rendered_image_uri = f"data:image/jpeg;base64,{base64_img}"
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Rendering failed: {str(e)}"
            )

    # Fetch product recommendations matching our context
    recommended_products = CatalogService.get_recommendations(db, context)

    # Save Bot response and applied settings to database
    applied_parts = []
    if compiled_options.get("lipstick_color") and compiled_options.get("lipstick_opacity", 0.0) > 0.0:
        applied_parts.append(f"lipstick: {compiled_options['lipstick_color']} ({int(compiled_options['lipstick_opacity']*100)}% opacity)")
    if compiled_options.get("blush_color") and compiled_options.get("blush_opacity", 0.0) > 0.0:
        applied_parts.append(f"blush: {compiled_options['blush_color']} ({int(compiled_options['blush_opacity']*100)}% opacity)")
    if compiled_options.get("foundation_color") and compiled_options.get("foundation_opacity", 0.0) > 0.0:
        applied_parts.append(f"foundation: {compiled_options['foundation_color']} ({int(compiled_options['foundation_opacity']*100)}% opacity)")
    if compiled_options.get("eyeshadow_color") and compiled_options.get("eyeshadow_opacity", 0.0) > 0.0:
        applied_parts.append(f"eyeshadow: {compiled_options['eyeshadow_color']} ({int(compiled_options['eyeshadow_opacity']*100)}% opacity)")
    if compiled_options.get("eyeliner_color") and compiled_options.get("eyeliner_opacity", 0.0) > 0.0:
        applied_parts.append(f"eyeliner: {compiled_options['eyeliner_color']} ({int(compiled_options['eyeliner_opacity']*100)}% opacity)")
    if compiled_options.get("eyebrow_color") and compiled_options.get("eyebrow_opacity", 0.0) > 0.0:
        applied_parts.append(f"eyebrows: {compiled_options['eyebrow_color']} ({int(compiled_options['eyebrow_opacity']*100)}% opacity)")
    
    if applied_parts:
        applied_desc = ", ".join(applied_parts)
        bot_response_text = f"I resolved the style to '{look_preset or 'Custom'}'. Here are the cosmetic settings I selected: {applied_desc}. Try-on updated!"
    else:
        bot_response_text = f"I resolved the style to '{look_preset or 'Custom'}'. No makeup changes were applied."

    bot_msg = ChatMessage(
        session_id=session_id,
        sender="bot",
        text=bot_response_text,
        applied_options=json.dumps(compiled_options)
    )
    db.add(bot_msg)
    db.commit()

    return {
        "detected_skin_tone": context.skin_tone,
        "detected_face_shape": context.face_shape,
        "resolved_preset": look_preset,
        "applied_options": compiled_options,
        "recommended_products": recommended_products,
        "rendered_image": rendered_image_uri,
        "bot_message": bot_response_text
    }
