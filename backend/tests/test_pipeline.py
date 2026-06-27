import unittest
import cv2
import os
from app.services.vision.face_analysis_service import FaceAnalysisService


class TestPipeline(unittest.TestCase):
    def setUp(self) -> None:
        self.face_service = FaceAnalysisService()
        # Path to lena.jpg at the workspace root
        self.image_path = r"d:\privet_pr\lena.jpg"

    def test_pipeline_integration(self) -> None:
        self.assertTrue(
            os.path.exists(self.image_path),
            f"Test image not found at {self.image_path}"
        )

        image = cv2.imread(self.image_path)
        self.assertIsNotNone(image, "Failed to load test image.")

        # Run analyze
        response = self.face_service.analyze(image)

        # Asserts
        self.assertTrue(response.face_detected)
        self.assertEqual(response.face_count, 1)
        self.assertEqual(response.landmark_count, 468)
        self.assertIn(response.skin_tone, ["Warm", "Cool", "Neutral"])
        self.assertIn(response.face_shape, ["Oval", "Round", "Square", "Heart", "Diamond", "Long"])

        print("\n--- Pipeline Execution Output ---")
        print(f"Face Detected: {response.face_detected}")
        print(f"Face Count: {response.face_count}")
        print(f"Landmark Count: {response.landmark_count}")
        print(f"Skin Tone: {response.skin_tone}")
        print(f"Face Shape: {response.face_shape}")
        print("---------------------------------")


if __name__ == "__main__":
    unittest.main()
