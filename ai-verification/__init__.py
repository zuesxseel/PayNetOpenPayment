"""
AI Verification System

A comprehensive Python-based identity verification system that uses artificial intelligence 
to verify identity documents, perform facial recognition, detect liveness, and cross-check 
with government databases.

This package provides:
- OCR text extraction from identity documents
- Document authenticity verification 
- Facial recognition and comparison
- Liveness detection and anti-spoofing
- Database cross-verification with government records
"""

from .main import ai_verification_service, ComprehensiveAIVerificationService
from .models.schemas import (
    VerificationInput, 
    ComprehensiveVerificationResult,
    DocumentType,
    VerificationStatus
)

__version__ = "1.0.0"
__author__ = "AI Verification Team"
__email__ = "support@aiverification.com"

__all__ = [
    "ai_verification_service",
    "ComprehensiveAIVerificationService",
    "VerificationInput",
    "ComprehensiveVerificationResult", 
    "DocumentType",
    "VerificationStatus"
] 