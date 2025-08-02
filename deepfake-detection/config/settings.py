"""
Deepfake Detection System Configuration
"""
import os
from typing import List, Dict, Any
from pydantic import BaseSettings, Field


class DeepfakeDetectionSettings(BaseSettings):
    """Main configuration for deepfake detection services"""
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8001, env="API_PORT")
    api_debug: bool = Field(default=False, env="API_DEBUG")
    
    # Security
    secret_key: str = Field(default="deepfake-detection-secret", env="SECRET_KEY")
    allowed_origins: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///deepfake_detection.db", env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # File Storage
    upload_folder: str = Field(default="uploads", env="UPLOAD_FOLDER")
    max_file_size: int = Field(default=100 * 1024 * 1024, env="MAX_FILE_SIZE")  # 100MB
    allowed_video_extensions: List[str] = Field(default=["mp4", "avi", "mov", "mkv"], env="ALLOWED_VIDEO_EXTENSIONS")
    allowed_image_extensions: List[str] = Field(default=["jpg", "jpeg", "png", "bmp"], env="ALLOWED_IMAGE_EXTENSIONS")
    allowed_audio_extensions: List[str] = Field(default=["wav", "mp3", "flac", "aac"], env="ALLOWED_AUDIO_EXTENSIONS")
    
    # Model Paths
    models_directory: str = Field(default="models", env="MODELS_DIRECTORY")
    face_detection_model: str = Field(default="retinaface", env="FACE_DETECTION_MODEL")  # retinaface, mtcnn, mediapipe
    deepfake_model: str = Field(default="ensemble", env="DEEPFAKE_MODEL")  # ensemble, xception, efficientnet
    
    # Detection Thresholds
    deepfake_threshold: float = Field(default=0.5, env="DEEPFAKE_THRESHOLD")
    confidence_threshold: float = Field(default=0.8, env="CONFIDENCE_THRESHOLD")
    face_quality_threshold: float = Field(default=0.6, env="FACE_QUALITY_THRESHOLD")
    
    # Video Processing
    max_frames_per_video: int = Field(default=100, env="MAX_FRAMES_PER_VIDEO")
    frame_extraction_interval: int = Field(default=5, env="FRAME_EXTRACTION_INTERVAL")  # Extract every Nth frame
    video_resolution_limit: int = Field(default=1080, env="VIDEO_RESOLUTION_LIMIT")
    
    # Audio Processing
    audio_sample_rate: int = Field(default=16000, env="AUDIO_SAMPLE_RATE")
    audio_chunk_duration: float = Field(default=3.0, env="AUDIO_CHUNK_DURATION")  # seconds
    
    # Performance Configuration
    use_gpu: bool = Field(default=True, env="USE_GPU")
    batch_size: int = Field(default=8, env="BATCH_SIZE")
    num_workers: int = Field(default=4, env="NUM_WORKERS")
    max_concurrent_requests: int = Field(default=10, env="MAX_CONCURRENT_REQUESTS")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/deepfake_detection.log", env="LOG_FILE")
    
    # Blockchain Configuration (for verification records)
    blockchain_enabled: bool = Field(default=False, env="BLOCKCHAIN_ENABLED")
    ethereum_rpc_url: str = Field(default="", env="ETHEREUM_RPC_URL")
    contract_address: str = Field(default="", env="CONTRACT_ADDRESS")
    private_key: str = Field(default="", env="PRIVATE_KEY")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class ModelConfig:
    """Model configuration and paths"""
    
    BASE_PATH = "models"
    
    # Face Detection Models
    RETINAFACE_MODEL = f"{BASE_PATH}/face_detection/retinaface_resnet50.pth"
    MTCNN_MODEL = f"{BASE_PATH}/face_detection/mtcnn"
    MEDIAPIPE_MODEL = f"{BASE_PATH}/face_detection/mediapipe"
    
    # Deepfake Detection Models
    XCEPTION_MODEL = f"{BASE_PATH}/deepfake/xception_deepfake.pth"
    EFFICIENTNET_MODEL = f"{BASE_PATH}/deepfake/efficientnet_b7_deepfake.pth"
    ENSEMBLE_MODELS = [
        f"{BASE_PATH}/deepfake/xception_deepfake.pth",
        f"{BASE_PATH}/deepfake/efficientnet_b7_deepfake.pth",
        f"{BASE_PATH}/deepfake/resnet_deepfake.pth"
    ]
    
    # Audio Deepfake Detection
    AUDIO_DEEPFAKE_MODEL = f"{BASE_PATH}/audio/audio_deepfake_detector.pth"
    
    # Feature Extraction Models
    FACENET_MODEL = f"{BASE_PATH}/features/facenet_pytorch.pth"
    ARCFACE_MODEL = f"{BASE_PATH}/features/arcface_resnet100.pth"


class ThresholdConfig:
    """Detection thresholds configuration"""
    
    # Deepfake Detection Thresholds
    DEEPFAKE_THRESHOLD = 0.5
    HIGH_CONFIDENCE_THRESHOLD = 0.8
    LOW_CONFIDENCE_THRESHOLD = 0.3
    
    # Face Quality Thresholds
    FACE_SIZE_MIN = 80  # pixels
    FACE_BLUR_THRESHOLD = 100
    FACE_BRIGHTNESS_MIN = 50
    FACE_BRIGHTNESS_MAX = 200
    
    # Video Analysis Thresholds
    MIN_FRAMES_FOR_ANALYSIS = 10
    CONSISTENCY_THRESHOLD = 0.7  # Consistency across frames
    TEMPORAL_CONSISTENCY = 0.6
    
    # Audio Analysis Thresholds
    AUDIO_DEEPFAKE_THRESHOLD = 0.5
    VOICE_AUTHENTICITY_THRESHOLD = 0.7


class FeatureConfig:
    """Feature extraction configuration"""
    
    # Visual Features
    VISUAL_FEATURES = [
        "texture_analysis",
        "frequency_domain",
        "eye_movement",
        "lip_sync",
        "facial_landmarks",
        "micro_expressions",
        "lighting_consistency",
        "compression_artifacts"
    ]
    
    # Audio Features
    AUDIO_FEATURES = [
        "spectral_features",
        "prosodic_features",
        "voice_biometrics",
        "breathing_patterns",
        "vocal_tract_features"
    ]
    
    # Temporal Features
    TEMPORAL_FEATURES = [
        "frame_consistency",
        "motion_patterns",
        "expression_continuity",
        "blink_patterns"
    ]


# Create global settings instance
settings = DeepfakeDetectionSettings()

# Export commonly used configurations
__all__ = [
    "settings",
    "ModelConfig", 
    "ThresholdConfig",
    "FeatureConfig"
] 