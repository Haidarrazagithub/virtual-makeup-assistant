import os
import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.utils.seed_products import seed_database


class TestRecommendation(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.image_path = r"d:\privet_pr\lena.jpg"

        # Seed the local SQLite catalog before every run
        seed_database()

    def test_list_products_endpoint(self) -> None:
        # Query product listing
        response = self.client.get("/api/v1/products")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data) > 0)

        # Check properties structure
        prod = data[0]
        self.assertIn("id", prod)
        self.assertIn("brand", prod)
        self.assertIn("name", prod)
        self.assertIn("category", prod)
        self.assertIn("hex_color", prod)
        self.assertIn("suitability", prod)

        # Test querying filters
        response_filtered = self.client.get("/api/v1/products?category=lipstick")
        self.assertEqual(response_filtered.status_code, 200)
        data_filtered = response_filtered.json()
        for p in data_filtered:
            self.assertEqual(p["category"], "lipstick")

        print("API list-products validated successfully.")

    def test_recommend_look_endpoint_presets(self) -> None:
        # Request matching "party" look with red lips overrides
        data = {
            "prompt": "I want a gorgeous party look with bold red lips"
        }
        with open(self.image_path, "rb") as img_file:
            files = {"image": ("lena.jpg", img_file, "image/jpeg")}
            response = self.client.post("/api/v1/recommend-look", data=data, files=files)

        self.assertEqual(response.status_code, 200)
        resp_json = response.json()

        # Assert extracted attributes
        self.assertIn("detected_skin_tone", resp_json)
        self.assertIn("detected_face_shape", resp_json)
        self.assertEqual(resp_json["resolved_preset"], "party")

        # Assert correct override color is matched
        self.assertEqual(resp_json["applied_options"]["lipstick_color"], "#E0115F")

        # Assert recommended database items exist
        self.assertIn("recommended_products", resp_json)
        self.assertIn("lipstick", resp_json["recommended_products"])
        self.assertIn("eyeshadow", resp_json["recommended_products"])

        # Assert generated preview image is returned in Base64 encoding
        self.assertIn("rendered_image", resp_json)
        self.assertTrue(resp_json["rendered_image"].startswith("data:image/jpeg;base64,"))

        print("API recommend-look presets validated successfully.")

    def test_recommend_look_endpoint_defaults(self) -> None:
        # Request default natural office lookup
        data = {
            "prompt": "Give me natural office makeup"
        }
        with open(self.image_path, "rb") as img_file:
            files = {"image": ("lena.jpg", img_file, "image/jpeg")}
            response = self.client.post("/api/v1/recommend-look", data=data, files=files)

        self.assertEqual(response.status_code, 200)
        resp_json = response.json()
        self.assertEqual(resp_json["resolved_preset"], "office")
        self.assertIn("rendered_image", resp_json)

        print("API recommend-look default office option validated successfully.")


if __name__ == "__main__":
    unittest.main()
