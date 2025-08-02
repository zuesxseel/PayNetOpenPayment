"""
Face Recognition Service for facial comparison and verification
"""
import cv2
import numpy as np
import face_recognition
import dlib
import time
from typing import List, Tuple, Optional, Dict
from loguru import logger
import mediapipe as mp

from ..models.schemas import (
    FaceRecognitionResult, DetectedFace, FaceLandmark, 
    FaceQuality, BoundingBox, Coordinates
)
from ..utils.image_utils import ImageProcessor
from ..config.settings import settings, ThresholdConfig


class FaceRecognitionService:
    """Face recognition service for identity verification"""
    
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        
        # Initialize dlib predictor if available
        self.dlib_predictor = None
        try:
            self.dlib_predictor = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")
        except Exception as e:
            logger.warning(f"Dlib predictor not available: {e}")
    
    def compare_faces(
        self, 
        document_image_base64: str, 
        selfie_image_base64: str
    ) -> FaceRecognitionResult:
        """
        Compare faces between document and selfie images
        
        Args:
            document_image_base64: Base64 encoded document image
            selfie_image_base64: Base64 encoded selfie image
            
        Returns:
            Face recognition result
        """
        start_time = time.time()
        
        try:
            # Convert images
            doc_image = ImageProcessor.base64_to_opencv(document_image_base64)
            selfie_image = ImageProcessor.base64_to_opencv(selfie_image_base64)
            
            # Preprocess images
            doc_image = ImageProcessor.preprocess_for_face_recognition(doc_image)
            selfie_image = ImageProcessor.preprocess_for_face_recognition(selfie_image)
            
            # Detect faces in both images
            doc_faces = self._detect_faces_in_image(doc_image)
            selfie_faces = self._detect_faces_in_image(selfie_image)
            
            if not doc_faces:
                return self._create_failed_result("No face detected in document image", start_time)
            
            if not selfie_faces:
                return self._create_failed_result("No face detected in selfie image", start_time)
            
            if len(doc_faces) > 1:
                return self._create_failed_result("Multiple faces detected in document image", start_time)
            
            if len(selfie_faces) > 1:
                return self._create_failed_result("Multiple faces detected in selfie image", start_time)
            
            # Get the primary faces
            doc_face = doc_faces[0]
            selfie_face = selfie_faces[0]
            
            # Check face quality
            doc_quality_ok = self._is_face_quality_acceptable(doc_face.quality)
            selfie_quality_ok = self._is_face_quality_acceptable(selfie_face.quality)
            
            if not doc_quality_ok:
                return self._create_failed_result("Document face quality too low", start_time)
            
            if not selfie_quality_ok:
                return self._create_failed_result("Selfie face quality too low", start_time)
            
            # Extract face encodings
            doc_encoding = self._extract_face_encoding(doc_image, doc_face)
            selfie_encoding = self._extract_face_encoding(selfie_image, selfie_face)
            
            if doc_encoding is None or selfie_encoding is None:
                return self._create_failed_result("Failed to extract face encodings", start_time)
            
            # Calculate similarity
            match_score = self._calculate_face_similarity(doc_encoding, selfie_encoding)
            is_match = match_score >= settings.face_match_threshold
            
            # Calculate confidence based on multiple factors
            confidence = self._calculate_confidence(match_score, doc_face.quality, selfie_face.quality)
            
            processing_time = time.time() - start_time
            
            return FaceRecognitionResult(
                success=True,
                is_match=is_match,
                match_score=match_score,
                confidence=confidence,
                threshold_used=settings.face_match_threshold,
                faces_detected=[doc_face, selfie_face],
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in face comparison: {e}")
            
            return FaceRecognitionResult(
                success=False,
                is_match=False,
                match_score=0.0,
                confidence=0.0,
                threshold_used=settings.face_match_threshold,
                faces_detected=[],
                processing_time=processing_time
            )
    
    def _detect_faces_in_image(self, image: np.ndarray) -> List[DetectedFace]:
        """
        Detect faces in image using MediaPipe
        
        Args:
            image: OpenCV image
            
        Returns:
            List of detected faces
        """
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            results = self.face_detection.process(rgb_image)
            
            detected_faces = []
            
            if results.detections:
                for detection in results.detections:
                    # Extract bounding box
                    bbox = self._extract_bounding_box(detection, image.shape)
                    
                    # Extract face region
                    face_region = self._extract_face_region(image, bbox)
                    
                    # Extract landmarks
                    landmarks = self._extract_face_landmarks(rgb_image, bbox)
                    
                    # Calculate face quality
                    quality = self._calculate_face_quality(face_region, landmarks)
                    
                    detected_face = DetectedFace(
                        bounding_box=bbox,
                        landmarks=landmarks,
                        quality=quality,
                        encoding=None  # Will be set later if needed
                    )
                    
                    detected_faces.append(detected_face)
            
            return detected_faces
            
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []
    
    def _extract_bounding_box(self, detection, image_shape) -> BoundingBox:
        """Extract bounding box from MediaPipe detection"""
        h, w, _ = image_shape
        
        bbox = detection.location_data.relative_bounding_box
        
        # Convert relative coordinates to absolute
        x = int(bbox.xmin * w)
        y = int(bbox.ymin * h)
        width = int(bbox.width * w)
        height = int(bbox.height * h)
        
        return BoundingBox(
            coordinates=Coordinates(x=x, y=y, width=width, height=height),
            confidence=detection.score[0],
            text=None
        )
    
    def _extract_face_region(self, image: np.ndarray, bbox: BoundingBox) -> np.ndarray:
        """Extract face region from image"""
        x = int(bbox.coordinates.x)
        y = int(bbox.coordinates.y)
        w = int(bbox.coordinates.width)
        h = int(bbox.coordinates.height)
        
        # Add padding
        padding = 20
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(image.shape[1] - x, w + 2 * padding)
        h = min(image.shape[0] - y, h + 2 * padding)
        
        return image[y:y+h, x:x+w]
    
    def _extract_face_landmarks(self, rgb_image: np.ndarray, bbox: BoundingBox) -> List[FaceLandmark]:
        """Extract facial landmarks"""
        try:
            # Use MediaPipe Face Mesh for detailed landmarks
            results = self.face_mesh.process(rgb_image)
            
            landmarks = []
            
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    # Convert normalized coordinates to pixel coordinates
                    h, w, _ = rgb_image.shape
                    
                    # Extract key landmarks (simplified set)
                    key_points = [33, 133, 362, 263, 1, 61, 291, 199]  # Eyes, nose, mouth corners
                    
                    for i, point_idx in enumerate(key_points):
                        if point_idx < len(face_landmarks.landmark):
                            landmark = face_landmarks.landmark[point_idx]
                            
                            landmarks.append(FaceLandmark(
                                type=f"point_{i}",
                                x=landmark.x * w,
                                y=landmark.y * h
                            ))
            
            return landmarks
            
        except Exception as e:
            logger.error(f"Error extracting landmarks: {e}")
            return []
    
    def _calculate_face_quality(self, face_region: np.ndarray, landmarks: List[FaceLandmark]) -> FaceQuality:
        """
        Calculate face quality metrics
        
        Args:
            face_region: Cropped face image
            landmarks: Facial landmarks
            
        Returns:
            Face quality metrics
        """
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            
            # Calculate brightness
            brightness = np.mean(gray)
            
            # Calculate sharpness using Laplacian variance
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Calculate blur using variance of Laplacian
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Estimate pose angles
            pose_angles = self._estimate_pose_angles(landmarks)
            
            # Calculate eye distance (face size indicator)
            eye_distance = self._calculate_eye_distance(landmarks)
            
            # Determine if face is frontal
            is_frontal = (
                abs(pose_angles["pitch"]) < 15 and
                abs(pose_angles["yaw"]) < 15 and
                abs(pose_angles["roll"]) < 15
            )
            
            return FaceQuality(
                brightness=float(brightness),
                sharpness=float(sharpness),
                blur_score=float(blur_score),
                pose_pitch=pose_angles["pitch"],
                pose_yaw=pose_angles["yaw"],
                pose_roll=pose_angles["roll"],
                eye_distance=eye_distance,
                is_frontal=is_frontal
            )
            
        except Exception as e:
            logger.error(f"Error calculating face quality: {e}")
            
            # Return default quality metrics
            return FaceQuality(
                brightness=128.0,
                sharpness=0.0,
                blur_score=0.0,
                pose_pitch=0.0,
                pose_yaw=0.0,
                pose_roll=0.0,
                eye_distance=0.0,
                is_frontal=False
            )
    
    def _estimate_pose_angles(self, landmarks: List[FaceLandmark]) -> Dict[str, float]:
        """Estimate head pose angles from landmarks"""
        try:
            if len(landmarks) < 4:
                return {"pitch": 0.0, "yaw": 0.0, "roll": 0.0}
            
            # Simple pose estimation based on landmark positions
            # This is a simplified version - in production, use more sophisticated methods
            
            # For now, return approximate values based on landmark spread
            return {
                "pitch": 0.0,  # Up/down tilt
                "yaw": 0.0,    # Left/right turn
                "roll": 0.0    # Head rotation
            }
            
        except Exception as e:
            logger.error(f"Error estimating pose: {e}")
            return {"pitch": 0.0, "yaw": 0.0, "roll": 0.0}
    
    def _calculate_eye_distance(self, landmarks: List[FaceLandmark]) -> float:
        """Calculate distance between eyes"""
        try:
            if len(landmarks) < 2:
                return 0.0
            
            # Simplified eye distance calculation
            # In a real implementation, you'd identify specific eye landmarks
            return 50.0  # Placeholder value
            
        except Exception as e:
            logger.error(f"Error calculating eye distance: {e}")
            return 0.0
    
    def _is_face_quality_acceptable(self, quality: FaceQuality) -> bool:
        """Check if face quality meets minimum requirements"""
        try:
            # Check brightness
            if quality.brightness < 50 or quality.brightness > 200:
                return False
            
            # Check sharpness
            if quality.sharpness < ThresholdConfig.FACE_QUALITY_MIN * 1000:
                return False
            
            # Check if face is too tilted
            if abs(quality.pose_pitch) > 30 or abs(quality.pose_yaw) > 30:
                return False
            
            # Check if face is frontal enough
            if not quality.is_frontal:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking face quality: {e}")
            return False
    
    def _extract_face_encoding(self, image: np.ndarray, face: DetectedFace) -> Optional[np.ndarray]:
        """
        Extract face encoding using face_recognition library
        
        Args:
            image: Original image
            face: Detected face information
            
        Returns:
            Face encoding array or None if failed
        """
        try:
            # Convert to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Get bounding box coordinates
            bbox = face.bounding_box.coordinates
            top = int(bbox.y)
            right = int(bbox.x + bbox.width)
            bottom = int(bbox.y + bbox.height)
            left = int(bbox.x)
            
            # Extract face encoding
            face_locations = [(top, right, bottom, left)]
            encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            if encodings:
                return encodings[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting face encoding: {e}")
            return None
    
    def _calculate_face_similarity(self, encoding1: np.ndarray, encoding2: np.ndarray) -> float:
        """
        Calculate similarity between two face encodings
        
        Args:
            encoding1: First face encoding
            encoding2: Second face encoding
            
        Returns:
            Similarity score (0-1)
        """
        try:
            # Calculate Euclidean distance
            distance = np.linalg.norm(encoding1 - encoding2)
            
            # Convert distance to similarity score (0-1)
            # Face recognition typically uses 0.6 as threshold for distance
            similarity = max(0, 1 - (distance / 0.6))
            
            return min(1.0, similarity)
            
        except Exception as e:
            logger.error(f"Error calculating face similarity: {e}")
            return 0.0
    
    def _calculate_confidence(
        self, 
        match_score: float, 
        doc_quality: FaceQuality, 
        selfie_quality: FaceQuality
    ) -> float:
        """
        Calculate overall confidence score
        
        Args:
            match_score: Face matching score
            doc_quality: Document face quality
            selfie_quality: Selfie face quality
            
        Returns:
            Confidence score (0-1)
        """
        try:
            # Base confidence from match score
            confidence = match_score
            
            # Adjust based on image quality
            quality_factor = min(
                doc_quality.sharpness / 1000.0,
                selfie_quality.sharpness / 1000.0
            )
            
            # Normalize quality factor
            quality_factor = min(1.0, quality_factor / 100.0)
            
            # Combine scores
            final_confidence = (confidence * 0.8) + (quality_factor * 0.2)
            
            return min(1.0, max(0.0, final_confidence))
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.0
    
    def _create_failed_result(self, error_message: str, start_time: float) -> FaceRecognitionResult:
        """Create a failed face recognition result"""
        processing_time = time.time() - start_time
        logger.warning(f"Face recognition failed: {error_message}")
        
        return FaceRecognitionResult(
            success=False,
            is_match=False,
            match_score=0.0,
            confidence=0.0,
            threshold_used=settings.face_match_threshold,
            faces_detected=[],
            processing_time=processing_time
        )
    
    def get_face_quality_feedback(self, quality: FaceQuality) -> List[str]:
        """
        Get user-friendly feedback on face quality
        
        Args:
            quality: Face quality metrics
            
        Returns:
            List of improvement suggestions
        """
        feedback = []
        
        if quality.brightness < 50:
            feedback.append("Image is too dark - use better lighting")
        elif quality.brightness > 200:
            feedback.append("Image is too bright - reduce lighting")
        
        if quality.sharpness < ThresholdConfig.FACE_QUALITY_MIN * 1000:
            feedback.append("Image is blurry - hold camera steady")
        
        if abs(quality.pose_pitch) > 15:
            feedback.append("Keep your head level (not tilted up or down)")
        
        if abs(quality.pose_yaw) > 15:
            feedback.append("Face the camera directly (not turned to side)")
        
        if abs(quality.pose_roll) > 15:
            feedback.append("Keep your head straight (not rotated)")
        
        if not quality.is_frontal:
            feedback.append("Position your face directly facing the camera")
        
        if quality.eye_distance < 30:
            feedback.append("Move closer to the camera")
        
        if not feedback:
            feedback.append("Face quality is good!")
        
        return feedback
    
    def detect_multiple_faces(self, image_base64: str) -> int:
        """
        Detect number of faces in image
        
        Args:
            image_base64: Base64 encoded image
            
        Returns:
            Number of faces detected
        """
        try:
            image = ImageProcessor.base64_to_opencv(image_base64)
            faces = self._detect_faces_in_image(image)
            return len(faces)
            
        except Exception as e:
            logger.error(f"Error detecting multiple faces: {e}")
            return 0 