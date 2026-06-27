from sqlalchemy.orm import Session
from app.models.product import Product
from app.services.vision.context import VisionContext


class CatalogService:
    """
    Handles matching products from the database catalog to facial attributes.
    """

    @staticmethod
    def get_recommendations(db: Session, context: VisionContext) -> dict:
        """
        Retrieves recommended products matching the user's skin tone suitability using VisionContext.
        Returns a dict of products grouped by their category.
        """
        skin_tone = context.skin_tone
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
                    "category": prod.category,
                    "hex_color": prod.hex_color,
                    "finish": prod.finish,
                    "suitability": prod.suitability,
                    "price": prod.price
                })

        return recommendations
