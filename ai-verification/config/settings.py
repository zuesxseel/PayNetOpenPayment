"""
AI Verification System Configuration
"""
import os
from typing import List, Dict, Any
from pydantic import BaseSettings, Field


class AIVerificationSettings(BaseSettings):
    """Main configuration for AI verification services"""
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_debug: bool = Field(default=False, env="API_DEBUG")
    
    # Security
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    allowed_origins: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///ai_verification.db", env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # File Storage
    upload_folder: str = Field(default="uploads", env="UPLOAD_FOLDER")
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    allowed_extensions: List[str] = Field(default=["jpg", "jpeg", "png", "pdf"], env="ALLOWED_EXTENSIONS")
    
    # OCR Configuration
    ocr_engine: str = Field(default="easyocr", env="OCR_ENGINE")  # easyocr, tesseract, paddleocr
    ocr_languages: List[str] = Field(default=["en", "ch_sim"], env="OCR_LANGUAGES")
    ocr_confidence_threshold: float = Field(default=0.7, env="OCR_CONFIDENCE_THRESHOLD")
    
    # Face Recognition Configuration
    face_recognition_model: str = Field(default="VGG-Face", env="FACE_RECOGNITION_MODEL")
    face_detection_backend: str = Field(default="opencv", env="FACE_DETECTION_BACKEND")
    face_match_threshold: float = Field(default=0.85, env="FACE_MATCH_THRESHOLD")
    face_quality_threshold: float = Field(default=0.6, env="FACE_QUALITY_THRESHOLD")
    
    # Liveness Detection Configuration
    liveness_model_path: str = Field(default="models/liveness_model.pkl", env="LIVENESS_MODEL_PATH")
    liveness_threshold: float = Field(default=0.8, env="LIVENESS_THRESHOLD")
    anti_spoofing_threshold: float = Field(default=0.7, env="ANTI_SPOOFING_THRESHOLD")
    
    # Document Verification Configuration
    document_templates_path: str = Field(default="models/document_templates", env="DOCUMENT_TEMPLATES_PATH")
    security_features_model: str = Field(default="models/security_features.pkl", env="SECURITY_FEATURES_MODEL")
    document_authenticity_threshold: float = Field(default=0.75, env="DOCUMENT_AUTHENTICITY_THRESHOLD")
    
    # Database Verification Configuration
    government_api_url: str = Field(default="https://api.gov.sg", env="GOVERNMENT_API_URL")
    government_api_key: str = Field(default="", env="GOVERNMENT_API_KEY")
    database_cache_ttl: int = Field(default=24 * 60 * 60, env="DATABASE_CACHE_TTL")  # 24 hours
    
    # Performance Configuration
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    retry_attempts: int = Field(default=3, env="RETRY_ATTEMPTS")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/ai_verification.log", env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class SingaporeDocumentConfig:
    """Singapore-specific document configuration"""
    
    NRIC_PATTERNS = {
        "format": r"^[STFG]\d{7}[A-Z]$",
        "prefixes": ["S", "T", "F", "G"],
        "checksum_weights": [2, 7, 6, 5, 4, 3, 2]
    }
    
    PASSPORT_PATTERNS = {
        "format": r"^[A-Z]\d{7}[A-Z]$",
        "mrz_format": r"P<SGP[A-Z0-9<]+",
        "validity_years": 10
    }
    
    DRIVING_LICENSE_PATTERNS = {
        "format": r"^S\d{7}[A-Z]$",
        "classes": ["1", "2", "2A", "2B", "3", "3A", "3C", "4", "5"]
    }
    
    SECURITY_FEATURES = {
        "nric": ["hologram", "microtext", "rfid", "watermark"],
        "passport": ["hologram", "watermark", "rfid", "security_thread"],
        "driving_license": ["hologram", "barcode", "microtext"]
    }


class ModelPaths:
    """Model file paths configuration"""
    
    BASE_PATH = "models"
    
    # Face Recognition Models
    FACE_RECOGNITION_MODEL = f"{BASE_PATH}/face_recognition/dlib_face_recognition_resnet_model_v1.dat"
    FACE_DETECTION_MODEL = f"{BASE_PATH}/face_detection/mmod_human_face_detector.dat"
    FACE_LANDMARKS_MODEL = f"{BASE_PATH}/face_landmarks/shape_predictor_68_face_landmarks.dat"
    
    # Liveness Detection Models
    LIVENESS_MODEL = f"{BASE_PATH}/liveness/liveness_model.pkl"
    ANTI_SPOOFING_MODEL = f"{BASE_PATH}/liveness/anti_spoofing_model.h5"
    
    # Document Verification Models
    DOCUMENT_CLASSIFIER = f"{BASE_PATH}/document/document_classifier.pkl"
    SECURITY_FEATURES_DETECTOR = f"{BASE_PATH}/document/security_features_model.h5"
    
    # OCR Models
    TESSERACT_CONFIG = f"{BASE_PATH}/ocr/tesseract_config.txt"
    EASYOCR_MODEL_DIR = f"{BASE_PATH}/ocr/easyocr"


class ThresholdConfig:
    """AI model thresholds configuration"""
    
    # OCR Thresholds
    OCR_CONFIDENCE = 0.7
    TEXT_EXTRACTION_MIN_LENGTH = 3
    
    # Face Recognition Thresholds
    FACE_MATCH_THRESHOLD = 0.85
    FACE_QUALITY_MIN = 0.6
    FACE_SIZE_MIN = 80  # pixels
    
    # Liveness Detection Thresholds
    LIVENESS_SCORE = 0.8
    ANTI_SPOOFING_SCORE = 0.7
    BLINK_DETECTION = 0.5
    
    # Document Verification Thresholds
    DOCUMENT_AUTHENTICITY = 0.75
    SECURITY_FEATURE_CONFIDENCE = 0.6
    TEMPLATE_MATCH_THRESHOLD = 0.8
    
    # Database Verification Thresholds
    NAME_MATCH_THRESHOLD = 0.9
    NRIC_VALIDATION_STRICT = True
    DATE_TOLERANCE_DAYS = 1


# Create global settings instance
settings = AIVerificationSettings()

# Export commonly used configurations
__all__ = [
    "settings",
    "SingaporeDocumentConfig", 
    "ModelPaths",
    "ThresholdConfig"
] 