import json
from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatMessageBase(BaseModel):
    sender: str  # "user" or "bot"
    text: str


class ChatMessageCreate(ChatMessageBase):
    applied_options: Optional[Dict[str, Any]] = None


class ChatMessageResponse(ChatMessageBase):
    id: int
    session_id: str
    created_at: datetime
    applied_options: Optional[Dict[str, Any]] = None

    @field_validator('applied_options', mode='before')
    @classmethod
    def parse_applied_options(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return None
        return v

    class Config:
        from_attributes = True


class ChatSessionBase(BaseModel):
    id: str


class ChatSessionCreate(ChatSessionBase):
    skin_tone: Optional[str] = None
    face_shape: Optional[str] = None


class ChatSessionResponse(ChatSessionBase):
    created_at: datetime
    skin_tone: Optional[str] = None
    face_shape: Optional[str] = None
    messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True


class ChatPromptRequest(BaseModel):
    prompt: str
