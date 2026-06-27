from dataclasses import dataclass, field
import numpy as np
from typing import Dict, List, Tuple, Any

@dataclass
class VisionContext:
    """
    Unified context container storing processed visual states, landmarks,
    detected attributes, and image layers passed across domain boundaries.
    """
    original_image: np.ndarray             # Raw BGR image
    rgb_image: np.ndarray                  # Pre-processed RGB image
    landmarks: List[Tuple[float, float]]   # 468 facial landmark coordinates (normalized)
    regions: Dict[str, List[Tuple[float, float]]] # Segmented feature coordinate arrays
    skin_tone: str                         # Skin undertone classification (Cool, Warm, Neutral)
    face_shape: str                        # Face shape classification (Oval, Round, etc.)
    face_count: int                        # Number of detected faces
    metadata: Dict[str, Any] = field(default_factory=dict) # Scalable storage bucket (lighting, pose, etc.)
