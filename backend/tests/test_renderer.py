import os
import unittest
import cv2
from fastapi.testclient import TestClient

from app.main import app
from app.services.vision.makeup_rendering_service import MakeupRenderingService
from app.services.vision.face_analysis_service import FaceAnalysisService


class TestRenderer(unittest.TestCase):
    def setUp(self) -> None:
        self.image_path = r"d:\privet_pr\lena.jpg"
        self.output_path = r"d:\privet_pr\virtual-makeup-assistant\backend\tests\rendered_lena_test.jpg"
        self.face_service = FaceAnalysisService()
        self.client = TestClient(app)

    def test_rendering_service(self) -> None:
        self.assertTrue(
            os.path.exists(self.image_path),
            f"Test image not found at {self.image_path}"
        )

        image = cv2.imread(self.image_path)
        self.assertIsNotNone(image, "Failed to load test image.")

        # Extract landmarks first
        response = self.face_service.analyze(image)
        self.assertTrue(response.face_detected)

        # Get the actual landmarks
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_service.face_mesh.process(rgb_image)
        self.assertTrue(results.multi_face_landmarks)
        
        from app.services.vision.landmark_service import LandmarkService
        landmarks = LandmarkService.get_all_landmarks(results.multi_face_landmarks[0].landmark)

        # Apply makeup options
        options = {
            "lipstick_color": "#FF0000",      # Red
            "lipstick_opacity": 0.6,
            "blush_color": "#FFC0CB",         # Pink
            "blush_opacity": 0.5,
            "foundation_color": "#F3D2C1",    # Beige/Skin
            "foundation_opacity": 0.4,
            "eyeshadow_color": "#800080",     # Purple
            "eyeshadow_opacity": 0.5,
            "eyeliner_color": "#000000",      # Black eyeliner
            "eyeliner_opacity": 0.7,
            "eyebrow_color": "#3D2B1F",       # Brown eyebrows
            "eyebrow_opacity": 0.4
        }

        rendered = MakeupRenderingService.apply_makeup(image, landmarks, options)
        
        # Save output image for developer review
        cv2.imwrite(self.output_path, rendered)
        self.assertTrue(os.path.exists(self.output_path), "Failed to save rendered output image.")
        self.assertEqual(rendered.shape, image.shape)
        print(f"\nSaved rendering output to: {self.output_path}")

    def test_api_endpoint_custom(self) -> None:
        # Prepare custom parameters
        data = {
            "lipstick_color": "#E0115F",
            "lipstick_opacity": "0.7",
            "blush_color": "#FE7D6A",
            "blush_opacity": "0.4",
            "foundation_color": "#EED5C4",
            "foundation_opacity": "0.3",
            "eyeshadow_color": "#4B0082",
            "eyeshadow_opacity": "0.5",
            "eyeliner_color": "#1C1C1C",
            "eyeliner_opacity": "0.6",
            "eyebrow_color": "#4A3B32",
            "eyebrow_opacity": "0.5",
        }

        with open(self.image_path, "rb") as img_file:
            files = {"image": ("lena.jpg", img_file, "image/jpeg")}
            response = self.client.post("/api/v1/render-makeup", data=data, files=files)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "image/jpeg")
        self.assertTrue(len(response.content) > 0)
        print("API render-makeup custom options validated.")

    def test_api_endpoint_presets(self) -> None:
        # 1. First, check that analyze-face returns preset recommendations
        with open(self.image_path, "rb") as img_file:
            files = {"image": ("lena.jpg", img_file, "image/jpeg")}
            response = self.client.post("/api/v1/analyze-face", files=files)

        self.assertEqual(response.status_code, 200)
        resp_json = response.json()
        self.assertIn("recommended_presets", resp_json)
        self.assertIsNotNone(resp_json["recommended_presets"])
        self.assertIn("office", resp_json["recommended_presets"])
        self.assertIn("party", resp_json["recommended_presets"])
        self.assertIn("bridal", resp_json["recommended_presets"])
        print("API analyze-face preset metadata validated.")

        # 2. Check rendering with preset
        data = {
            "look_preset": "office",
        }
        with open(self.image_path, "rb") as img_file:
            files = {"image": ("lena.jpg", img_file, "image/jpeg")}
            response = self.client.post("/api/v1/render-makeup", data=data, files=files)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "image/jpeg")
        self.assertTrue(len(response.content) > 0)
        print("API render-makeup presets validated.")

    def test_api_endpoint_invalid_color_error(self) -> None:
        # Verify that sending an invalid color format raises a 400 HTTPException
        data = {
            "look_preset": "party",
            "lipstick_color": "string",
        }
        with open(self.image_path, "rb") as img_file:
            files = {"image": ("lena.jpg", img_file, "image/jpeg")}
            response = self.client.post("/api/v1/render-makeup", data=data, files=files)

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid color parameter format", response.json()["detail"])
        print("API render-makeup invalid color handling validated successfully (returned 400 Bad Request).")


if __name__ == "__main__":
    unittest.main()


