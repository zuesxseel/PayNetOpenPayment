"""
Visual Deepfake Detection Service
"""
import cv2
import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
import time
from typing import List, Dict, Optional, Tuple, Any
from loguru import logger
import mediapipe as mp

from ..models.schemas import (
    DetectionResult, VisualFeatures, FaceInfo, BoundingBox, 
    FrameAnalysis, AuthenticityLevel, DetectionMethod
)
from ..utils.media_utils import MediaProcessor
from ..config.settings import settings, ThresholdConfig


class VisualDeepfakeDetector:
    """Visual deepfake detection service"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() and settings.use_gpu else 'cpu')
        self.face_detector = None
        self.deepfake_model = None
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize detection models"""
        try:
            # Initialize face detection (MediaPipe)
            self.face_detector = mp.solutions.face_detection.FaceDetection(
                model_selection=1, min_detection_confidence=0.5
            )
            
            # Initialize deepfake detection model (EfficientNet)
            self.deepfake_model = models.efficientnet_b0(pretrained=True)
            self.deepfake_model.classifier = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(self.deepfake_model.classifier[1].in_features, 2)
            )
            self.deepfake_model = self.deepfake_model.to(self.device)
            self.deepfake_model.eval()
            
            logger.info("Visual deepfake detection models initialized")
            
        except Exception as e:
            logger.error(f"Error initializing visual models: {e}")
    
    def detect_deepfake_in_image(self, image: np.ndarray) -> DetectionResult:
        """Detect deepfake in a single image"""
        start_time = time.time()
        
        try:
            # Detect faces
            faces = self._detect_faces(image)
            
            if not faces:
                return self._create_no_face_result(start_time)
            
            # Process each face
            deepfake_probabilities = []
            visual_features_list = []
            
            for face in faces:
                face_patch = self._extract_face_patch(image, face.bbox)
                if face_patch is not None:
                    # Run deepfake detection
                    preprocessed = self._preprocess_face(face_patch)
                    prob = self._run_deepfake_model(preprocessed)
                    deepfake_probabilities.append(prob)
                    
                    # Extract visual features
                    features = self._extract_visual_features(face_patch)
                    visual_features_list.append(features)
            
            # Combine results
            overall_probability = max(deepfake_probabilities) if deepfake_probabilities else 0.0
            combined_features = self._combine_visual_features(visual_features_list)
            
            # Determine authenticity and confidence
            authenticity_level = self._determine_authenticity_level(overall_probability)
            confidence = self._calculate_confidence(overall_probability, combined_features)
            
            return DetectionResult(
                method=DetectionMethod.VISUAL_ANALYSIS,
                probability=float(overall_probability),
                confidence=float(confidence),
                authenticity_level=authenticity_level,
                processing_time=time.time() - start_time,
                features=combined_features
            )
            
        except Exception as e:
            logger.error(f"Error in visual deepfake detection: {e}")
            return self._create_error_result(start_time)
    
    def detect_deepfake_in_frames(self, frames: List[np.ndarray]) -> List[FrameAnalysis]:
        """Detect deepfake in video frames"""
        frame_results = []
        
        for i, frame in enumerate(frames):
            try:
                faces = self._detect_faces(frame)
                detection_result = self.detect_deepfake_in_image(frame)
                
                frame_analysis = FrameAnalysis(
                    frame_number=i,
                    timestamp=i / 30.0,
                    faces=faces,
                    deepfake_probability=detection_result.probability,
                    authenticity_level=detection_result.authenticity_level,
                    anomalies=[],
                    features=detection_result.features.__dict__ if detection_result.features else {}
                )
                
                frame_results.append(frame_analysis)
                
            except Exception as e:
                logger.error(f"Error processing frame {i}: {e}")
                continue
        
        return frame_results
    
    def _detect_faces(self, image: np.ndarray) -> List[FaceInfo]:
        """Detect faces in image using MediaPipe"""
        try:
            faces = []
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.face_detector.process(rgb_image)
            
            if results.detections:
                h, w = image.shape[:2]
                for detection in results.detections:
                    bbox_data = detection.location_data.relative_bounding_box
                    
                    bbox = BoundingBox(
                        x=float(bbox_data.xmin * w),
                        y=float(bbox_data.ymin * h),
                        width=float(bbox_data.width * w),
                        height=float(bbox_data.height * h),
                        confidence=detection.score[0]
                    )
                    
                    face_info = FaceInfo(
                        bbox=bbox,
                        landmarks=[],
                        quality_score=self._calculate_face_quality(image, bbox),
                        pose_angles={}
                    )
                    faces.append(face_info)
            
            return faces
            
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []
    
    def _extract_face_patch(self, image: np.ndarray, bbox: BoundingBox) -> Optional[np.ndarray]:
        """Extract and resize face patch"""
        try:
            x, y, w, h = int(bbox.x), int(bbox.y), int(bbox.width), int(bbox.height)
            
            # Add padding
            padding = 0.2
            pad_x, pad_y = int(w * padding), int(h * padding)
            
            x = max(0, x - pad_x)
            y = max(0, y - pad_y)
            w = min(image.shape[1] - x, w + 2 * pad_x)
            h = min(image.shape[0] - y, h + 2 * pad_y)
            
            face_patch = image[y:y+h, x:x+w]
            face_patch = cv2.resize(face_patch, (224, 224))
            
            return face_patch
            
        except Exception as e:
            logger.error(f"Error extracting face patch: {e}")
            return None
    
    def _preprocess_face(self, face_patch: np.ndarray) -> torch.Tensor:
        """Preprocess face for model input"""
        try:
            rgb_patch = cv2.cvtColor(face_patch, cv2.COLOR_BGR2RGB)
            
            transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            tensor = transform(rgb_patch).unsqueeze(0)
            return tensor.to(self.device)
            
        except Exception as e:
            logger.error(f"Error preprocessing face: {e}")
            return torch.zeros(1, 3, 224, 224).to(self.device)
    
    def _run_deepfake_model(self, preprocessed_face: torch.Tensor) -> float:
        """Run deepfake detection model"""
        try:
            with torch.no_grad():
                output = self.deepfake_model(preprocessed_face)
                prob = torch.softmax(output, dim=1)[0, 1].cpu().item()
                return prob
                
        except Exception as e:
            logger.error(f"Error running deepfake model: {e}")
            return 0.5
    
    def _extract_visual_features(self, face_patch: np.ndarray) -> VisualFeatures:
        """Extract visual features for analysis"""
        try:
            gray = cv2.cvtColor(face_patch, cv2.COLOR_BGR2GRAY)
            
            # Texture analysis
            texture_inconsistency = float(np.var(gray) / 10000.0)
            
            # Frequency analysis
            f_transform = np.fft.fft2(gray)
            magnitude = np.abs(f_transform)
            frequency_artifacts = float(np.mean(magnitude) / 1000.0)
            
            # Compression artifacts
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            compression_artifacts = float(laplacian.var() / 1000.0)
            
            # Lighting consistency
            lighting_consistency = float(np.std(gray) / 100.0)
            
            return VisualFeatures(
                texture_inconsistency=min(1.0, texture_inconsistency),
                frequency_artifacts=min(1.0, frequency_artifacts),
                eye_movement_patterns=0.0,
                lip_sync_accuracy=0.0,
                facial_landmark_stability=0.0,
                micro_expression_analysis=0.0,
                lighting_consistency=min(1.0, lighting_consistency),
                compression_artifacts=min(1.0, compression_artifacts)
            )
            
        except Exception as e:
            logger.error(f"Error extracting visual features: {e}")
            return self._default_visual_features()
    
    def _calculate_face_quality(self, image: np.ndarray, bbox: BoundingBox) -> float:
        """Calculate face quality score"""
        try:
            x, y, w, h = int(bbox.x), int(bbox.y), int(bbox.width), int(bbox.height)
            face_region = image[y:y+h, x:x+w]
            
            if face_region.size == 0:
                return 0.0
            
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            
            # Sharpness
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(1.0, sharpness / 1000.0)
            
            # Brightness
            brightness = np.mean(gray)
            brightness_score = 1.0 - abs(brightness - 128) / 128.0
            
            # Contrast
            contrast = np.std(gray)
            contrast_score = min(1.0, contrast / 50.0)
            
            return float((sharpness_score + brightness_score + contrast_score) / 3.0)
            
        except Exception as e:
            logger.error(f"Error calculating face quality: {e}")
            return 0.0
    
    def _combine_visual_features(self, features_list: List[VisualFeatures]) -> VisualFeatures:
        """Combine visual features from multiple faces"""
        if not features_list:
            return self._default_visual_features()
        
        return VisualFeatures(
            texture_inconsistency=max(f.texture_inconsistency for f in features_list),
            frequency_artifacts=max(f.frequency_artifacts for f in features_list),
            eye_movement_patterns=max(f.eye_movement_patterns for f in features_list),
            lip_sync_accuracy=max(f.lip_sync_accuracy for f in features_list),
            facial_landmark_stability=max(f.facial_landmark_stability for f in features_list),
            micro_expression_analysis=max(f.micro_expression_analysis for f in features_list),
            lighting_consistency=max(f.lighting_consistency for f in features_list),
            compression_artifacts=max(f.compression_artifacts for f in features_list)
        )
    
    def _determine_authenticity_level(self, probability: float) -> AuthenticityLevel:
        """Determine authenticity level from probability"""
        if probability >= ThresholdConfig.HIGH_CONFIDENCE_THRESHOLD:
            return AuthenticityLevel.DEEPFAKE
        elif probability >= ThresholdConfig.DEEPFAKE_THRESHOLD:
            return AuthenticityLevel.LIKELY_FAKE
        elif probability >= ThresholdConfig.LOW_CONFIDENCE_THRESHOLD:
            return AuthenticityLevel.SUSPICIOUS
        else:
            return AuthenticityLevel.LIKELY_AUTHENTIC
    
    def _calculate_confidence(self, probability: float, features: VisualFeatures) -> float:
        """Calculate confidence in detection"""
        base_confidence = abs(probability - 0.5) * 2
        feature_consistency = 1.0 - np.std([
            features.texture_inconsistency,
            features.frequency_artifacts,
            features.lighting_consistency,
            features.compression_artifacts
        ])
        return min(1.0, max(0.0, (base_confidence + feature_consistency) / 2.0))
    
    def _default_visual_features(self) -> VisualFeatures:
        """Create default visual features"""
        return VisualFeatures(
            texture_inconsistency=0.0,
            frequency_artifacts=0.0,
            eye_movement_patterns=0.0,
            lip_sync_accuracy=0.0,
            facial_landmark_stability=0.0,
            micro_expression_analysis=0.0,
            lighting_consistency=0.0,
            compression_artifacts=0.0
        )
    
    def _create_no_face_result(self, start_time: float) -> DetectionResult:
        """Create result when no faces detected"""
        return DetectionResult(
            method=DetectionMethod.VISUAL_ANALYSIS,
            probability=0.0,
            confidence=0.0,
            authenticity_level=AuthenticityLevel.AUTHENTIC,
            processing_time=time.time() - start_time,
            features=self._default_visual_features()
        )
    
    def _create_error_result(self, start_time: float) -> DetectionResult:
        """Create result on error"""
        return DetectionResult(
            method=DetectionMethod.VISUAL_ANALYSIS,
            probability=0.5,
            confidence=0.0,
            authenticity_level=AuthenticityLevel.SUSPICIOUS,
            processing_time=time.time() - start_time,
            features=self._default_visual_features()
        ) 