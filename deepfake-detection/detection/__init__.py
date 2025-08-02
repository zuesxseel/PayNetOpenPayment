"""Detection modules for deepfake analysis"""

from .visual_detector import VisualDeepfakeDetector
from .audio_detector import AudioDeepfakeDetector

__all__ = [
    "VisualDeepfakeDetector",
    "AudioDeepfakeDetector"
] 