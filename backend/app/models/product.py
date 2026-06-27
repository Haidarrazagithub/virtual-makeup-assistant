from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base


class Product(Base):
    """
    SQLAlchemy database model representing virtual makeup catalog products.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)     # lipstick, blush, eyeshadow, eyeliner, foundation, eyebrows
    hex_color = Column(String, nullable=False)
    finish = Column(String, nullable=False)        # Matte, Satin, Glossy
    suitability = Column(String, nullable=False)   # Warm, Cool, Neutral (skin-tone suitability)
    price = Column(Float, nullable=False)
