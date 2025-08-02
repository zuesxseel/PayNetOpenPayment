"""
Pydantic models for AI verification system
"""
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator


class DocumentType(str, Enum):
    """Supported document types"""
    NRIC = "nric"
    PASSPORT = "passport"
    DRIVING_LICENSE = "driving_license"


class VerificationStatus(str, Enum):
    """Verification status options"""
    PENDING = "pending"
    PROCESSING = "processing"
    PASSED = "passed"
    FAILED = "failed"
    REVIEW_REQUIRED = "review_required"
    ERROR = "error"


class SecurityFeatureType(str, Enum):
    """Security feature types"""
    HOLOGRAM = "hologram"
    WATERMARK = "watermark"
    MICROTEXT = "microtext"
    RFID = "rfid"
    BARCODE = "barcode"
    MAGNETIC_STRIPE = "magnetic_stripe"
    SECURITY_THREAD = "security_thread"


class SpoofingType(str, Enum):
    """Spoofing attack types"""
    PHOTO = "photo"
    VIDEO = "video"
    MASK = "mask"
    DEEPFAKE = "deepfake"
    SCREEN = "screen"


# Base Models
class BaseResponse(BaseModel):
    """Base response model"""
    success: bool
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str


class Coordinates(BaseModel):
    """Coordinate model for bounding boxes"""
    x: float
    y: float
    width: float
    height: float


class BoundingBox(BaseModel):
    """Bounding box with confidence"""
    coordinates: Coordinates
    confidence: float
    text: Optional[str] = None


# OCR Models
class ExtractedData(BaseModel):
    """Extracted data from documents"""
    name: Optional[str] = None
    nric: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    nationality: Optional[str] = None
    gender: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    document_number: Optional[str] = None


class OCRResult(BaseModel):
    """OCR processing result"""
    success: bool
    confidence: float
    extracted_data: ExtractedData
    raw_text: str
    bounding_boxes: List[BoundingBox] = []
    processing_time: float
    engine_used: str


# Face Recognition Models
class FaceLandmark(BaseModel):
    """Face landmark point"""
    type: str
    x: float
    y: float


class FaceQuality(BaseModel):
    """Face quality metrics"""
    brightness: float
    sharpness: float
    blur_score: float
    pose_pitch: float
    pose_yaw: float
    pose_roll: float
    eye_distance: float
    is_frontal: bool


class DetectedFace(BaseModel):
    """Detected face information"""
    bounding_box: BoundingBox
    landmarks: List[FaceLandmark]
    quality: FaceQuality
    encoding: Optional[List[float]] = None


class FaceRecognitionResult(BaseModel):
    """Face recognition result"""
    success: bool
    is_match: bool
    match_score: float
    confidence: float
    threshold_used: float
    faces_detected: List[DetectedFace]
    processing_time: float


# Liveness Detection Models
class SpoofingAttempt(BaseModel):
    """Detected spoofing attempt"""
    type: SpoofingType
    confidence: float
    detected: bool
    details: Dict[str, Any] = {}


class LivenessResult(BaseModel):
    """Liveness detection result"""
    success: bool
    is_live: bool
    liveness_score: float
    confidence: float
    spoofing_attempts: List[SpoofingAttempt]
    blink_detected: bool
    motion_detected: bool
    processing_time: float


# Document Verification Models
class SecurityFeature(BaseModel):
    """Security feature detection result"""
    type: SecurityFeatureType
    present: bool
    valid: bool
    confidence: float
    location: Optional[BoundingBox] = None


class DocumentVerificationResult(BaseModel):
    """Document verification result"""
    success: bool
    is_authentic: bool
    confidence: float
    document_type: DocumentType
    issuer: str
    security_features: List[SecurityFeature]
    template_match_score: float
    tampering_detected: bool
    processing_time: float


# Database Verification Models
class FieldMatch(BaseModel):
    """Individual field matching result"""
    field: str
    input_value: str
    database_value: str
    is_match: bool
    confidence: float


class DatabaseRecord(BaseModel):
    """Database record match"""
    source: str
    match_score: float
    field_matches: List[FieldMatch]
    last_updated: Optional[datetime] = None


class DatabaseVerificationResult(BaseModel):
    """Database verification result"""
    success: bool
    is_valid: bool
    verification_status: str
    matched_records: List[DatabaseRecord]
    blacklist_check: bool
    sanctions_check: bool
    processing_time: float


# Comprehensive Verification Models
class VerificationInput(BaseModel):
    """Input for verification process"""
    document_image: str  # Base64 encoded
    selfie_image: str   # Base64 encoded
    document_type: DocumentType
    metadata: Optional[Dict[str, Any]] = {}
    
    @validator('document_image', 'selfie_image')
    def validate_base64_image(cls, v):
        """Validate base64 image format"""
        if not v or not isinstance(v, str):
            raise ValueError("Image must be a base64 encoded string")
        return v


class VerificationProgress(BaseModel):
    """Verification progress update"""
    step: str
    status: VerificationStatus
    progress: float  # 0-100
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict[str, Any]] = None


class ComprehensiveVerificationResult(BaseModel):
    """Complete verification result"""
    verification_id: str
    timestamp: datetime
    success: bool
    overall_score: float
    status: VerificationStatus
    
    # Individual results
    ocr_result: Optional[OCRResult] = None
    face_recognition_result: Optional[FaceRecognitionResult] = None
    liveness_result: Optional[LivenessResult] = None
    document_verification_result: Optional[DocumentVerificationResult] = None
    database_verification_result: Optional[DatabaseVerificationResult] = None
    
    # Summary
    errors: List[str] = []
    warnings: List[str] = []
    recommendations: List[str] = []
    total_processing_time: float
    
    # Metadata
    input_metadata: Optional[Dict[str, Any]] = None
    model_versions: Dict[str, str] = {}


# API Request/Response Models
class VerificationRequest(BaseModel):
    """API request for verification"""
    input_data: VerificationInput
    options: Optional[Dict[str, Any]] = {}


class VerificationResponse(BaseResponse):
    """API response for verification"""
    result: Optional[ComprehensiveVerificationResult] = None


class QuickVerificationRequest(BaseModel):
    """Quick verification request (OCR + Face only)"""
    document_image: str
    selfie_image: str
    document_type: DocumentType


class QuickVerificationResult(BaseModel):
    """Quick verification result"""
    verification_id: str
    success: bool
    ocr_result: OCRResult
    face_recognition_result: FaceRecognitionResult
    processing_time: float


# Health Check Models
class ServiceHealth(BaseModel):
    """Individual service health status"""
    service: str
    status: str
    response_time: float
    error: Optional[str] = None


class SystemHealth(BaseModel):
    """Overall system health"""
    status: str
    services: List[ServiceHealth]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Statistics Models
class VerificationStats(BaseModel):
    """Verification statistics"""
    total_verifications: int
    successful_verifications: int
    failed_verifications: int
    average_processing_time: float
    success_rate: float
    common_failure_reasons: Dict[str, int]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Error Models
class ValidationError(BaseModel):
    """Validation error details"""
    field: str
    message: str
    invalid_value: Any


class ErrorResponse(BaseResponse):
    """Error response model"""
    error_code: str
    details: Optional[List[ValidationError]] = None


# Configuration Models
class ModelConfig(BaseModel):
    """Model configuration"""
    model_name: str
    version: str
    path: str
    loaded: bool
    last_updated: datetime


class SystemConfig(BaseModel):
    """System configuration overview"""
    models: List[ModelConfig]
    thresholds: Dict[str, float]
    settings: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow) 