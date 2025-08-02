"""Data models and schemas for AI verification system"""

from .schemas import *

__all__ = [
    "VerificationInput",
    "ComprehensiveVerificationResult", 
    "VerificationProgress",
    "DocumentType",
    "VerificationStatus",
    "OCRResult",
    "FaceRecognitionResult",
    "LivenessResult", 
    "DocumentVerificationResult",
    "DatabaseVerificationResult",
    "ExtractedData",
    "SecurityFeature",
    "SpoofingAttempt"
] 