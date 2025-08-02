"""
Pydantic models for deepfake detection system
"""
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator


class MediaType(str, Enum):
    """Supported media types"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class DetectionMethod(str, Enum):
    """Detection methods"""
    VISUAL_ANALYSIS = "visual_analysis"
    AUDIO_ANALYSIS = "audio_analysis"
    TEMPORAL_ANALYSIS = "temporal_analysis"
    ENSEMBLE = "ensemble"


class DeepfakeType(str, Enum):
    """Types of deepfake techniques"""
    FACE_SWAP = "face_swap"
    FACE_REENACTMENT = "face_reenactment"
    SPEECH_SYNTHESIS = "speech_synthesis"
    FULL_BODY_PUPPETRY = "full_body_puppetry"
    UNKNOWN = "unknown"


class AuthenticityLevel(str, Enum):
    """Authenticity levels"""
    AUTHENTIC = "authentic"
    LIKELY_AUTHENTIC = "likely_authentic"
    SUSPICIOUS = "suspicious"
    LIKELY_FAKE = "likely_fake"
    DEEPFAKE = "deepfake"


class ProcessingStatus(str, Enum):
    """Processing status options"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "error"


# Base Models
class BaseResponse(BaseModel):
    """Base response model"""
    success: bool
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str


class MediaInfo(BaseModel):
    """Media file information"""
    file_type: MediaType
    file_size: int
    duration: Optional[float] = None  # For video/audio
    resolution: Optional[str] = None  # For video/image
    fps: Optional[float] = None  # For video
    sample_rate: Optional[int] = None  # For audio
    channels: Optional[int] = None  # For audio


class BoundingBox(BaseModel):
    """Bounding box coordinates"""
    x: float
    y: float
    width: float
    height: float
    confidence: float


class FaceInfo(BaseModel):
    """Face detection information"""
    bbox: BoundingBox
    landmarks: List[Dict[str, float]] = []
    quality_score: float
    pose_angles: Dict[str, float] = {}
    expression: Optional[str] = None


class FrameAnalysis(BaseModel):
    """Individual frame analysis result"""
    frame_number: int
    timestamp: float
    faces: List[FaceInfo]
    deepfake_probability: float
    authenticity_level: AuthenticityLevel
    anomalies: List[str] = []
    features: Dict[str, float] = {}


class AudioSegmentAnalysis(BaseModel):
    """Audio segment analysis result"""
    start_time: float
    end_time: float
    deepfake_probability: float
    authenticity_level: AuthenticityLevel
    voice_features: Dict[str, float] = {}
    anomalies: List[str] = []


class VisualFeatures(BaseModel):
    """Visual feature analysis"""
    texture_inconsistency: float
    frequency_artifacts: float
    eye_movement_patterns: float
    lip_sync_accuracy: float
    facial_landmark_stability: float
    micro_expression_analysis: float
    lighting_consistency: float
    compression_artifacts: float


class AudioFeatures(BaseModel):
    """Audio feature analysis"""
    spectral_features: Dict[str, float]
    prosodic_features: Dict[str, float]
    voice_biometrics: Dict[str, float]
    breathing_patterns: float
    vocal_tract_features: Dict[str, float]
    speech_naturalness: float


class TemporalFeatures(BaseModel):
    """Temporal consistency analysis"""
    frame_consistency: float
    motion_patterns: float
    expression_continuity: float
    blink_patterns: float
    identity_consistency: float
    temporal_artifacts: float


class DetectionResult(BaseModel):
    """Individual detection method result"""
    method: DetectionMethod
    probability: float
    confidence: float
    authenticity_level: AuthenticityLevel
    processing_time: float
    features: Optional[Union[VisualFeatures, AudioFeatures, TemporalFeatures]] = None


class DeepfakeAnalysis(BaseModel):
    """Comprehensive deepfake analysis result"""
    detection_id: str
    timestamp: datetime
    media_info: MediaInfo
    
    # Overall Results
    is_deepfake: bool
    overall_probability: float
    confidence_score: float
    authenticity_level: AuthenticityLevel
    detected_techniques: List[DeepfakeType] = []
    
    # Individual Method Results
    visual_analysis: Optional[DetectionResult] = None
    audio_analysis: Optional[DetectionResult] = None
    temporal_analysis: Optional[DetectionResult] = None
    ensemble_result: Optional[DetectionResult] = None
    
    # Detailed Analysis
    frame_analysis: List[FrameAnalysis] = []
    audio_segments: List[AudioSegmentAnalysis] = []
    
    # Quality Metrics
    media_quality: Dict[str, float] = {}
    processing_quality: Dict[str, float] = {}
    
    # Anomalies and Evidence
    anomalies: List[str] = []
    evidence: List[str] = []
    artifacts: List[str] = []
    
    # Performance Metrics
    total_processing_time: float
    model_versions: Dict[str, str] = {}
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = None


class DeepfakeDetectionRequest(BaseModel):
    """Request for deepfake detection"""
    media_data: str  # Base64 encoded media
    media_type: MediaType
    detection_methods: List[DetectionMethod] = [DetectionMethod.ENSEMBLE]
    options: Optional[Dict[str, Any]] = {}
    
    @validator('media_data')
    def validate_media_data(cls, v):
        """Validate media data format"""
        if not v or not isinstance(v, str):
            raise ValueError("Media data must be a base64 encoded string")
        return v


class DeepfakeDetectionResponse(BaseResponse):
    """Response for deepfake detection"""
    result: Optional[DeepfakeAnalysis] = None


class BatchDetectionRequest(BaseModel):
    """Batch detection request"""
    media_items: List[DeepfakeDetectionRequest]
    batch_options: Optional[Dict[str, Any]] = {}


class BatchDetectionResponse(BaseResponse):
    """Batch detection response"""
    results: List[DeepfakeAnalysis] = []
    batch_summary: Dict[str, Any] = {}


class RealTimeDetectionRequest(BaseModel):
    """Real-time detection request"""
    stream_url: Optional[str] = None
    media_chunk: Optional[str] = None  # Base64 chunk
    chunk_type: MediaType
    session_id: str


class RealTimeDetectionResponse(BaseResponse):
    """Real-time detection response"""
    session_id: str
    chunk_result: DeepfakeAnalysis
    stream_summary: Optional[Dict[str, Any]] = None


class VerificationRecord(BaseModel):
    """Blockchain verification record"""
    detection_id: str
    timestamp: datetime
    content_hash: str
    authenticity_level: AuthenticityLevel
    signature: str
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None


class ModelPerformance(BaseModel):
    """Model performance metrics"""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    processing_speed: float  # fps or samples/sec
    memory_usage: float  # MB
    last_updated: datetime


class SystemHealth(BaseModel):
    """System health status"""
    status: str
    gpu_available: bool
    gpu_memory_usage: float
    cpu_usage: float
    memory_usage: float
    active_sessions: int
    queue_length: int
    models_loaded: List[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DetectionStats(BaseModel):
    """Detection statistics"""
    total_detections: int
    deepfakes_detected: int
    authentic_media: int
    detection_rate: float
    average_processing_time: float
    common_techniques: Dict[DeepfakeType, int]
    accuracy_metrics: Dict[str, float]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TrainingData(BaseModel):
    """Training data information"""
    dataset_name: str
    dataset_size: int
    data_types: List[MediaType]
    deepfake_techniques: List[DeepfakeType]
    quality_metrics: Dict[str, float]
    last_updated: datetime


class ModelConfig(BaseModel):
    """Model configuration"""
    model_name: str
    model_type: str
    version: str
    path: str
    loaded: bool
    performance: Optional[ModelPerformance] = None
    training_data: Optional[TrainingData] = None


class ErrorResponse(BaseResponse):
    """Error response model"""
    error_code: str
    error_type: str
    details: Optional[Dict[str, Any]] = None


class ValidationError(BaseModel):
    """Validation error details"""
    field: str
    message: str
    invalid_value: Any


class DetailedErrorResponse(ErrorResponse):
    """Detailed error response"""
    validation_errors: Optional[List[ValidationError]] = None
    stack_trace: Optional[str] = None


# Progress tracking
class DetectionProgress(BaseModel):
    """Detection progress update"""
    detection_id: str
    status: ProcessingStatus
    progress: float  # 0-100
    current_step: str
    estimated_time_remaining: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Advanced features
class TamperingAnalysis(BaseModel):
    """Tampering analysis result"""
    is_tampered: bool
    tampering_type: List[str] = []
    confidence: float
    tampered_regions: List[BoundingBox] = []
    evidence: List[str] = []


class BiometricConsistency(BaseModel):
    """Biometric consistency analysis"""
    identity_consistency: float
    facial_features_stability: float
    voice_consistency: float  # For videos with audio
    behavioral_patterns: float
    anomalies: List[str] = []


class ComprehensiveAnalysis(DeepfakeAnalysis):
    """Extended analysis with advanced features"""
    tampering_analysis: Optional[TamperingAnalysis] = None
    biometric_consistency: Optional[BiometricConsistency] = None
    provenance_analysis: Optional[Dict[str, Any]] = None
    forensic_markers: List[str] = [] 