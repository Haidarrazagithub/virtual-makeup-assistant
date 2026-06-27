from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.core.database import Base


class SavedLook(Base):
    """
    SQLAlchemy model representing a saved/bookmarked virtual makeup look.
    Maps a user-given name to full visual slider parameters.
    """
    __tablename__ = "saved_looks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Makeup settings
    lipstick_color = Column(String, nullable=True)
    lipstick_opacity = Column(Float, default=0.0)
    blush_color = Column(String, nullable=True)
    blush_opacity = Column(Float, default=0.0)
    foundation_color = Column(String, nullable=True)
    foundation_opacity = Column(Float, default=0.0)
    eyeshadow_color = Column(String, nullable=True)
    eyeshadow_opacity = Column(Float, default=0.0)
    eyeliner_color = Column(String, nullable=True)
    eyeliner_opacity = Column(Float, default=0.0)
    eyebrow_color = Column(String, nullable=True)
    eyebrow_opacity = Column(Float, default=0.0)
