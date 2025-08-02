"""
Deepfake Detection System

A comprehensive Python-based deepfake detection system that uses advanced AI and machine learning 
techniques to identify synthetic and manipulated media content including images, videos, and audio.

This package provides:
- Visual deepfake detection using CNN-based models and texture analysis
- Audio deepfake detection using LSTM models and spectral analysis  
- Temporal consistency analysis for video content
- Ensemble methods combining multiple detection approaches
- Real-time processing and batch analysis capabilities
- Blockchain integration for content verification
"""

from .main import deepfake_detector, ComprehensiveDeepfakeDetector
from .models.schemas import (
    DeepfakeDetectionRequest,
    DeepfakeAnalysis,
    MediaType,
    DetectionMethod,
    AuthenticityLevel,
    DeepfakeType,
    ProcessingStatus
)

__version__ = "1.0.0"
__author__ = "Deepfake Detection Team"
__email__ = "support@deepfakedetection.com"

__all__ = [
    "deepfake_detector",
    "ComprehensiveDeepfakeDetector",
    "DeepfakeDetectionRequest",
    "DeepfakeAnalysis",
    "MediaType",
    "DetectionMethod",
    "AuthenticityLevel",
    "DeepfakeType",
    "ProcessingStatus"
] 