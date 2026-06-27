import uuid
import json
import base64
import cv2
import io
import mediapipe as mp
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
from app.services.vision.landmark_service import LandmarkService
from app.services.vision.skin_tone_service import SkinToneService
from app.services.vision.face_shape_service import FaceShapeService
from app.services.vision.makeup_rendering_service import MakeupRenderingService
from app.services.recommendation.recommendation_service import RecommendationService
from app.services.recommendation.genai_service import GenAIService

router = APIRouter()

face_mesh = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5
)


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
        # Update details if provided
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
        # Create session on the fly
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
    queries the Gemini LLM model, saves the resolved makeup values, and renders
    the options if an image is provided.
    """
    # 1. Fetch or create session
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        session = ChatSession(id=session_id)
        db.add(session)
        db.commit()
        db.refresh(session)

    # 2. Extract skin tone & face shape from active image if provided
    skin_tone = session.skin_tone or "Neutral"
    face_shape = session.face_shape or "Oval"
    img_cv = None
    landmarks = None

    if image:
        await ImageValidator.validate(image)
        image_bytes = await image.read()
        img_cv = ImageService.decode(image_bytes)
        
        rgb_img = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_img)
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0].landmark
            landmarks = LandmarkService.get_all_landmarks(face_landmarks)
            skin_tone = SkinToneService.detect_skin_tone(img_cv, landmarks)
            face_shape = FaceShapeService.detect_face_shape(landmarks)
            
            # Save tone and shape to session history
            session.skin_tone = skin_tone
            session.face_shape = face_shape
            db.commit()

    # 3. Read previous 6 messages for conversational context
    history_msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(6)
        .all()
    )
    # Reverse so they are chronological
    history_msgs.reverse()

    # 4. Save User prompt to database
    user_msg = ChatMessage(
        session_id=session_id,
        sender="user",
        text=prompt
    )
    db.add(user_msg)
    db.commit()

    # 5. Query LLM with history context
    genai_opts = await GenAIService.translate_prompt(prompt, skin_tone, face_shape, history_msgs)

    # 6. Compile makeup options (presets + overrides)
    look_preset = genai_opts.get("look_preset")
    base_opts = {}
    if look_preset:
        from app.constants.presets import PRESETS
        base_opts = PRESETS.get(skin_tone, {}).get(look_preset, {})

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

    # 7. Render makeup overlay if image is loaded
    rendered_image_uri = None
    if img_cv is not None and landmarks:
        try:
            rendered_img = MakeupRenderingService.apply_makeup(img_cv, landmarks, compiled_options)
            success, encoded_img = cv2.imencode(".jpg", rendered_img)
            if success:
                base64_img = base64.b64encode(encoded_img.tobytes()).decode("utf-8")
                rendered_image_uri = f"data:image/jpeg;base64,{base64_img}"
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Rendering failed: {str(e)}"
            )

    # 8. Fetch product recommendations
    recommended_products = RecommendationService.get_recommendations(db, skin_tone, face_shape)

    # 9. Save Bot response and applied settings to database
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
        "detected_skin_tone": skin_tone,
        "detected_face_shape": face_shape,
        "resolved_preset": look_preset,
        "applied_options": compiled_options,
        "recommended_products": recommended_products,
        "rendered_image": rendered_image_uri,
        "bot_message": bot_response_text
    }
