from app.core.database import Base, engine, SessionLocal
from app.models.product import Product


def seed_database() -> None:
    # Create tables if they do not exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Clear existing entries
        db.query(Product).delete()

        products = [
            # --- Cool Skin Tone Products ---
            Product(brand="MAC", name="Ruby Red Matte", category="lipstick", hex_color="#800020", finish="Matte", suitability="Cool", price=22.0),
            Product(brand="Maybelline", name="Soft Rosewood Gloss", category="lipstick", hex_color="#DFA8A8", finish="Glossy", suitability="Cool", price=9.5),
            Product(brand="NARS", name="Cherry Blossom Stain", category="lipstick", hex_color="#B76E79", finish="Satin", suitability="Cool", price=28.0),

            Product(brand="Clinique", name="Cherry Pink Matte Blush", category="blush", hex_color="#C71585", finish="Matte", suitability="Cool", price=26.0),
            Product(brand="Benefit", name="Dandelion Pink Glow", category="blush", hex_color="#FFC0CB", finish="Satin", suitability="Cool", price=32.0),

            Product(brand="Urban Decay", name="Lavender Pearl Shimmer", category="eyeshadow", hex_color="#E6E6FA", finish="Glossy", suitability="Cool", price=19.0),
            Product(brand="Anastasia", name="Royal Violet Metallic", category="eyeshadow", hex_color="#4B0082", finish="Glossy", suitability="Cool", price=25.0),

            Product(brand="Fenty Beauty", name="Pro Filt'r Porcelain Cool", category="foundation", hex_color="#F3D2C1", finish="Matte", suitability="Cool", price=40.0),

            Product(brand="Bobbi Brown", name="Midnight Black Fluid Eyeliner", category="eyeliner", hex_color="#000000", finish="Matte", suitability="Cool", price=27.0),
            Product(brand="NYX", name="Ash Brown Eyebrow Gel", category="eyebrows", hex_color="#2C1E1A", finish="Matte", suitability="Cool", price=8.0),

            # --- Warm Skin Tone Products ---
            Product(brand="NARS", name="Coral Glow Satin", category="lipstick", hex_color="#E9967A", finish="Satin", suitability="Warm", price=28.0),
            Product(brand="L'Oreal", name="Sunset Orange Matte", category="lipstick", hex_color="#FF4500", finish="Matte", suitability="Warm", price=10.5),
            Product(brand="Chanel", name="Warm Terracotta Velvet", category="lipstick", hex_color="#D2691E", finish="Matte", suitability="Warm", price=45.0),

            Product(brand="NARS", name="Peach Luster Blush", category="blush", hex_color="#F4A460", finish="Satin", suitability="Warm", price=30.0),
            Product(brand="Milani", name="Baked Bronzer Glow", category="blush", hex_color="#CD853F", finish="Glossy", suitability="Warm", price=11.0),

            Product(brand="Urban Decay", name="Sandy Gold Glossy Eyeshadow", category="eyeshadow", hex_color="#DEB887", finish="Glossy", suitability="Warm", price=19.0),
            Product(brand="Too Faced", name="Honey Bronze Shimmer", category="eyeshadow", hex_color="#B8860B", finish="Glossy", suitability="Warm", price=24.0),

            Product(brand="Estee Lauder", name="Double Wear Warm Sand", category="foundation", hex_color="#ECD2B9", finish="Matte", suitability="Warm", price=48.0),

            Product(brand="L'Oreal", name="Deep Espresso Pencil Eyeliner", category="eyeliner", hex_color="#5C4033", finish="Matte", suitability="Warm", price=9.0),
            Product(brand="Anastasia", name="Warm Walnut Brow Wiz", category="eyebrows", hex_color="#3D2B1F", finish="Matte", suitability="Warm", price=23.0),

            # --- Neutral Skin Tone Products ---
            Product(brand="Maybelline", name="Dusty Mauve Satin", category="lipstick", hex_color="#C08081", finish="Satin", suitability="Neutral", price=9.5),
            Product(brand="MAC", name="Velvet Teddy Nude", category="lipstick", hex_color="#C8A2C8", finish="Matte", suitability="Neutral", price=22.0),
            Product(brand="Dior", name="Rouge Classic Crimson", category="lipstick", hex_color="#DC143C", finish="Satin", suitability="Neutral", price=46.0),

            Product(brand="Clinique", name="Orchid Sheer Cheek", category="blush", hex_color="#E6A8D7", finish="Satin", suitability="Neutral", price=26.0),
            Product(brand="NARS", name="Muted Rose Blush", category="blush", hex_color="#E6C7C2", finish="Matte", suitability="Neutral", price=30.0),

            Product(brand="Anastasia", name="Rosy Brown Matte Eyeshadow", category="eyeshadow", hex_color="#BC8F8F", finish="Matte", suitability="Neutral", price=15.0),
            Product(brand="MAC", name="Charcoal Shimmer Pigment", category="eyeshadow", hex_color="#708090", finish="Glossy", suitability="Neutral", price=22.0),

            Product(brand="Fenty Beauty", name="Pro Filt'r Neutral Beige", category="foundation", hex_color="#EED5C4", finish="Matte", suitability="Neutral", price=40.0),

            Product(brand="Benefit", name="Charcoal Grey Eyeliner", category="eyeliner", hex_color="#333333", finish="Matte", suitability="Neutral", price=24.0),
            Product(brand="Benefit", name="Gimme Brow Neutral Grey", category="eyebrows", hex_color="#262626", finish="Matte", suitability="Neutral", price=26.0),
        ]

        db.add_all(products)
        db.commit()
        print("Successfully seeded database with virtual makeup products catalog!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
