from sqlalchemy.orm import Session
from app.models.product import Product


class RecommendationService:
    """
    Handles matching products from the database catalog to facial attributes.
    """

    @staticmethod
    def get_recommendations(db: Session, skin_tone: str, face_shape: str) -> dict:
        """
        Retrieves recommended products matching the user's skin tone suitability.
        Returns a dict of products grouped by their category.
        """
        # Query products matching the user's skin tone, or Neutral (which works for all skin tones)
        products = db.query(Product).filter(
            Product.suitability.in_([skin_tone, "Neutral"])
        ).all()

        recommendations = {
            "lipstick": [],
            "blush": [],
            "eyeshadow": [],
            "foundation": [],
            "eyeliner": [],
            "eyebrows": []
        }

        for prod in products:
            if prod.category in recommendations:
                recommendations[prod.category].append({
                    "id": prod.id,
                    "brand": prod.brand,
                    "name": prod.name,
                    "hex_color": prod.hex_color,
                    "finish": prod.finish,
                    "price": prod.price
                })

        return recommendations
