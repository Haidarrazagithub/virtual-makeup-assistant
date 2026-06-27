from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class ChatSession(Base):
    """
    SQLAlchemy model representing a user chat session.
    Tracks detected face characteristics for personalization.
    """
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, index=True) # UUID string
    created_at = Column(DateTime, default=datetime.utcnow)
    skin_tone = Column(String, nullable=True)
    face_shape = Column(String, nullable=True)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """
    SQLAlchemy model representing a conversational turn in a session.
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String, nullable=False) # "user" or "bot"
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Store JSON-serialized resolved makeup options applied at this turn
    applied_options = Column(Text, nullable=True)

    session = relationship("ChatSession", back_populates="messages")
