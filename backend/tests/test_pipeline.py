import unittest
import cv2
import os
import numpy as np
from fastapi import HTTPException
from app.services.vision.pipeline import VisionPipeline
from app.services.vision.face_analysis_service import FaceAnalysisService


class TestPipeline(unittest.TestCase):
    def setUp(self) -> None:
        self.pipeline = VisionPipeline()
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

        # Run pipeline directly
        result = self.pipeline.process(image)

        # Asserts
        self.assertEqual(result.face_count, 1)
        self.assertEqual(len(result.landmarks), 468)
        self.assertIn(result.skin_tone, ["Warm", "Cool", "Neutral"])
        self.assertIn(result.face_shape, ["Oval", "Round", "Square", "Heart", "Diamond", "Long"])

        # Run analyze wrapper
        response = self.face_service.analyze(result)
        self.assertTrue(response.face_detected)
        self.assertEqual(response.landmark_count, 468)

        print("\n--- Pipeline Execution Output ---")
        print(f"Face Count: {result.face_count}")
        print(f"Landmark Count: {len(result.landmarks)}")
        print(f"Skin Tone: {result.skin_tone}")
        print(f"Face Shape: {result.face_shape}")
        print("---------------------------------")

    def test_empty_image_error(self) -> None:
        # Create an empty black image where no face exists
        empty_img = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with self.assertRaises(HTTPException) as ctx:
            self.pipeline.process(empty_img)
        
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("No face detected", ctx.exception.detail)

    def test_invalid_face_count_error(self) -> None:
        # Create an invalid tiny image size
        tiny_img = np.zeros((1, 1, 3), dtype=np.uint8)
        
        with self.assertRaises(HTTPException) as ctx:
            self.pipeline.process(tiny_img)
            
        self.assertEqual(ctx.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
