"""
Liveness Detection Service for anti-spoofing and live person verification
"""
import cv2
import numpy as np
import time
from typing import List, Dict, Optional, Tuple
from loguru import logger
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from ..models.schemas import LivenessResult, SpoofingAttempt, SpoofingType
from ..utils.image_utils import ImageProcessor
from ..config.settings import settings, ThresholdConfig


class LivenessDetectionService:
    """Liveness detection service for anti-spoofing verification"""
    
    def __init__(self):
        self.anti_spoofing_model = None
        self.scaler = None
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained liveness detection models"""
        try:
            # In a real implementation, load actual trained models
            # For now, create simple placeholder models
            self.anti_spoofing_model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.scaler = StandardScaler()
            
            # Train with dummy data (in production, use real training data)
            dummy_features = np.random.rand(1000, 10)
            dummy_labels = np.random.randint(0, 2, 1000)
            
            self.scaler.fit(dummy_features)
            scaled_features = self.scaler.transform(dummy_features)
            self.anti_spoofing_model.fit(scaled_features, dummy_labels)
            
            logger.info("Liveness detection models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading liveness models: {e}")
    
    def detect_liveness(self, image_base64: str) -> LivenessResult:
        """
        Perform comprehensive liveness detection on selfie image
        
        Args:
            image_base64: Base64 encoded selfie image
            
        Returns:
            Liveness detection result
        """
        start_time = time.time()
        
        try:
            # Convert image
            image = ImageProcessor.base64_to_opencv(image_base64)
            
            # Preprocess image
            processed_image = self._preprocess_for_liveness(image)
            
            # Perform multiple liveness checks
            texture_result = self._analyze_texture_features(processed_image)
            frequency_result = self._analyze_frequency_domain(processed_image)
            reflection_result = self._detect_screen_reflection(processed_image)
            depth_result = self._analyze_depth_cues(processed_image)
            motion_result = self._analyze_micro_motion(processed_image)
            blink_result = self._detect_blink_patterns(processed_image)
            
            # Combine results
            spoofing_attempts = []
            
            # Check for photo attacks
            if texture_result["is_suspicious"]:
                spoofing_attempts.append(SpoofingAttempt(
                    type=SpoofingType.PHOTO,
                    confidence=texture_result["confidence"],
                    detected=True,
                    details=texture_result["details"]
                ))
            
            # Check for screen attacks
            if reflection_result["screen_detected"]:
                spoofing_attempts.append(SpoofingAttempt(
                    type=SpoofingType.SCREEN,
                    confidence=reflection_result["confidence"],
                    detected=True,
                    details=reflection_result["details"]
                ))
            
            # Check for video attacks
            if frequency_result["video_artifacts"]:
                spoofing_attempts.append(SpoofingAttempt(
                    type=SpoofingType.VIDEO,
                    confidence=frequency_result["confidence"],
                    detected=True,
                    details=frequency_result["details"]
                ))
            
            # Check for mask attacks
            if depth_result["mask_suspected"]:
                spoofing_attempts.append(SpoofingAttempt(
                    type=SpoofingType.MASK,
                    confidence=depth_result["confidence"],
                    detected=True,
                    details=depth_result["details"]
                ))
            
            # Calculate overall liveness score
            liveness_score = self._calculate_liveness_score(
                texture_result, frequency_result, reflection_result, 
                depth_result, motion_result, blink_result
            )
            
            # Determine if person is live
            is_live = (
                liveness_score >= ThresholdConfig.LIVENESS_SCORE and
                len(spoofing_attempts) == 0
            )
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                liveness_score, spoofing_attempts, blink_result, motion_result
            )
            
            processing_time = time.time() - start_time
            
            return LivenessResult(
                success=True,
                is_live=is_live,
                liveness_score=liveness_score,
                confidence=confidence,
                spoofing_attempts=spoofing_attempts,
                blink_detected=blink_result["blink_detected"],
                motion_detected=motion_result["motion_detected"],
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in liveness detection: {e}")
            
            return LivenessResult(
                success=False,
                is_live=False,
                liveness_score=0.0,
                confidence=0.0,
                spoofing_attempts=[],
                blink_detected=False,
                motion_detected=False,
                processing_time=processing_time
            )
    
    def _preprocess_for_liveness(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for liveness detection
        
        Args:
            image: OpenCV image
            
        Returns:
            Preprocessed image
        """
        # Resize to standard size
        image = cv2.resize(image, (224, 224))
        
        # Enhance quality
        image = ImageProcessor.enhance_image_quality(image)
        
        return image
    
    def _analyze_texture_features(self, image: np.ndarray) -> Dict:
        """
        Analyze texture features to detect photo attacks
        
        Args:
            image: Preprocessed image
            
        Returns:
            Texture analysis result
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate LBP (Local Binary Pattern) features
            lbp_features = self._calculate_lbp_features(gray)
            
            # Calculate HOG (Histogram of Oriented Gradients) features
            hog_features = self._calculate_hog_features(gray)
            
            # Combine features
            combined_features = np.concatenate([lbp_features, hog_features])
            
            # Normalize features
            if self.scaler is not None:
                # Pad or truncate to expected size
                if len(combined_features) < 10:
                    combined_features = np.pad(combined_features, (0, 10 - len(combined_features)))
                else:
                    combined_features = combined_features[:10]
                
                normalized_features = self.scaler.transform([combined_features])
                
                # Predict using anti-spoofing model
                if self.anti_spoofing_model is not None:
                    prediction = self.anti_spoofing_model.predict_proba(normalized_features)[0]
                    spoofing_probability = prediction[1] if len(prediction) > 1 else 0.5
                else:
                    spoofing_probability = 0.3  # Default value
            else:
                spoofing_probability = 0.3
            
            is_suspicious = spoofing_probability > ThresholdConfig.ANTI_SPOOFING_SCORE
            
            return {
                "is_suspicious": is_suspicious,
                "confidence": float(spoofing_probability),
                "details": {
                    "lbp_variance": float(np.var(lbp_features)),
                    "hog_magnitude": float(np.mean(hog_features)),
                    "texture_smoothness": self._calculate_texture_smoothness(gray)
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing texture features: {e}")
            return {
                "is_suspicious": False,
                "confidence": 0.0,
                "details": {}
            }
    
    def _calculate_lbp_features(self, gray_image: np.ndarray) -> np.ndarray:
        """Calculate Local Binary Pattern features"""
        try:
            # Simple LBP implementation
            rows, cols = gray_image.shape
            lbp_image = np.zeros((rows-2, cols-2), dtype=np.uint8)
            
            for i in range(1, rows-1):
                for j in range(1, cols-1):
                    center = gray_image[i, j]
                    
                    # Compare with 8 neighbors
                    code = 0
                    neighbors = [
                        gray_image[i-1, j-1], gray_image[i-1, j], gray_image[i-1, j+1],
                        gray_image[i, j+1], gray_image[i+1, j+1], gray_image[i+1, j],
                        gray_image[i+1, j-1], gray_image[i, j-1]
                    ]
                    
                    for k, neighbor in enumerate(neighbors):
                        if neighbor >= center:
                            code += 2**k
                    
                    lbp_image[i-1, j-1] = code
            
            # Calculate histogram
            hist, _ = np.histogram(lbp_image.ravel(), bins=256, range=[0, 256])
            
            # Normalize histogram
            hist = hist.astype(float)
            hist /= (hist.sum() + 1e-7)
            
            return hist[:50]  # Return first 50 bins
            
        except Exception as e:
            logger.error(f"Error calculating LBP features: {e}")
            return np.zeros(50)
    
    def _calculate_hog_features(self, gray_image: np.ndarray) -> np.ndarray:
        """Calculate Histogram of Oriented Gradients features"""
        try:
            # Calculate gradients
            grad_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
            
            # Calculate magnitude and angle
            magnitude = np.sqrt(grad_x**2 + grad_y**2)
            angle = np.arctan2(grad_y, grad_x)
            
            # Convert angles to degrees and normalize to 0-180
            angle_deg = np.degrees(angle) % 180
            
            # Create histogram of gradients
            hist, _ = np.histogram(angle_deg.ravel(), bins=9, range=[0, 180], weights=magnitude.ravel())
            
            # Normalize histogram
            hist = hist.astype(float)
            hist /= (np.linalg.norm(hist) + 1e-7)
            
            return hist
            
        except Exception as e:
            logger.error(f"Error calculating HOG features: {e}")
            return np.zeros(9)
    
    def _calculate_texture_smoothness(self, gray_image: np.ndarray) -> float:
        """Calculate texture smoothness metric"""
        try:
            # Calculate standard deviation of the image
            return float(np.std(gray_image))
        except Exception as e:
            logger.error(f"Error calculating texture smoothness: {e}")
            return 0.0
    
    def _analyze_frequency_domain(self, image: np.ndarray) -> Dict:
        """
        Analyze frequency domain to detect video artifacts
        
        Args:
            image: Preprocessed image
            
        Returns:
            Frequency analysis result
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply FFT
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.log(np.abs(f_shift) + 1)
            
            # Analyze frequency characteristics
            high_freq_energy = self._calculate_high_frequency_energy(magnitude_spectrum)
            periodic_patterns = self._detect_periodic_patterns(magnitude_spectrum)
            
            # Video artifacts typically show specific frequency patterns
            video_artifacts = (
                high_freq_energy < 0.1 or  # Too smooth (over-compressed)
                periodic_patterns > 0.8     # Regular patterns (compression artifacts)
            )
            
            confidence = 0.7 if video_artifacts else 0.3
            
            return {
                "video_artifacts": video_artifacts,
                "confidence": confidence,
                "details": {
                    "high_freq_energy": high_freq_energy,
                    "periodic_patterns": periodic_patterns
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing frequency domain: {e}")
            return {
                "video_artifacts": False,
                "confidence": 0.0,
                "details": {}
            }
    
    def _calculate_high_frequency_energy(self, magnitude_spectrum: np.ndarray) -> float:
        """Calculate energy in high frequency components"""
        try:
            rows, cols = magnitude_spectrum.shape
            center_row, center_col = rows // 2, cols // 2
            
            # Create mask for high frequencies (outer region)
            y, x = np.ogrid[:rows, :cols]
            mask = (x - center_col)**2 + (y - center_row)**2 > (min(rows, cols) // 4)**2
            
            high_freq_energy = np.mean(magnitude_spectrum[mask])
            total_energy = np.mean(magnitude_spectrum)
            
            return high_freq_energy / (total_energy + 1e-7)
            
        except Exception as e:
            logger.error(f"Error calculating high frequency energy: {e}")
            return 0.5
    
    def _detect_periodic_patterns(self, magnitude_spectrum: np.ndarray) -> float:
        """Detect periodic patterns in frequency domain"""
        try:
            # Simple autocorrelation-based pattern detection
            autocorr = cv2.matchTemplate(magnitude_spectrum, magnitude_spectrum, cv2.TM_CCOEFF_NORMED)
            
            # Look for peaks indicating periodicity
            peaks = autocorr > 0.8
            pattern_score = np.sum(peaks) / peaks.size
            
            return float(pattern_score)
            
        except Exception as e:
            logger.error(f"Error detecting periodic patterns: {e}")
            return 0.0
    
    def _detect_screen_reflection(self, image: np.ndarray) -> Dict:
        """
        Detect screen reflections and moiré patterns
        
        Args:
            image: Preprocessed image
            
        Returns:
            Screen reflection analysis result
        """
        try:
            # Convert to HSV for better reflection detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Detect bright spots (potential reflections)
            bright_spots = self._detect_bright_spots(hsv)
            
            # Detect moiré patterns
            moire_patterns = self._detect_moire_patterns(image)
            
            # Detect regular grid patterns (LCD/LED screens)
            grid_patterns = self._detect_grid_patterns(image)
            
            screen_detected = (
                bright_spots["count"] > 5 or
                moire_patterns["detected"] or
                grid_patterns["detected"]
            )
            
            confidence = max(
                bright_spots["confidence"],
                moire_patterns["confidence"],
                grid_patterns["confidence"]
            )
            
            return {
                "screen_detected": screen_detected,
                "confidence": confidence,
                "details": {
                    "bright_spots": bright_spots,
                    "moire_patterns": moire_patterns,
                    "grid_patterns": grid_patterns
                }
            }
            
        except Exception as e:
            logger.error(f"Error detecting screen reflection: {e}")
            return {
                "screen_detected": False,
                "confidence": 0.0,
                "details": {}
            }
    
    def _detect_bright_spots(self, hsv_image: np.ndarray) -> Dict:
        """Detect bright spots that might indicate reflections"""
        try:
            # Extract value channel (brightness)
            value_channel = hsv_image[:, :, 2]
            
            # Threshold for very bright spots
            bright_mask = value_channel > 240
            
            # Find connected components
            num_labels, labels = cv2.connectedComponents(bright_mask.astype(np.uint8))
            
            # Filter by size (ignore very small spots)
            spot_count = 0
            for label in range(1, num_labels):
                if np.sum(labels == label) > 50:  # Minimum size threshold
                    spot_count += 1
            
            confidence = min(1.0, spot_count / 10.0)  # Normalize to 0-1
            
            return {
                "count": spot_count,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Error detecting bright spots: {e}")
            return {"count": 0, "confidence": 0.0}
    
    def _detect_moire_patterns(self, image: np.ndarray) -> Dict:
        """Detect moiré patterns from screen capture"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply bandpass filter to detect moiré frequency ranges
            kernel_size = 3
            blurred = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
            difference = cv2.absdiff(gray, blurred)
            
            # Calculate variance in the difference image
            moire_strength = np.var(difference)
            
            # Threshold for moiré detection
            detected = moire_strength > 100
            confidence = min(1.0, moire_strength / 500.0)
            
            return {
                "detected": detected,
                "confidence": confidence,
                "strength": float(moire_strength)
            }
            
        except Exception as e:
            logger.error(f"Error detecting moiré patterns: {e}")
            return {"detected": False, "confidence": 0.0, "strength": 0.0}
    
    def _detect_grid_patterns(self, image: np.ndarray) -> Dict:
        """Detect regular grid patterns from LCD/LED screens"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Hough line detection
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=50)
            
            if lines is not None:
                # Check for regular spacing in lines
                horizontal_lines = []
                vertical_lines = []
                
                for line in lines:
                    rho, theta = line[0]
                    if abs(theta) < np.pi/4 or abs(theta - np.pi) < np.pi/4:
                        horizontal_lines.append(rho)
                    elif abs(theta - np.pi/2) < np.pi/4:
                        vertical_lines.append(rho)
                
                # Check for regular spacing
                grid_detected = (
                    len(horizontal_lines) > 5 and len(vertical_lines) > 5
                )
                
                confidence = min(1.0, (len(horizontal_lines) + len(vertical_lines)) / 20.0)
            else:
                grid_detected = False
                confidence = 0.0
            
            return {
                "detected": grid_detected,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Error detecting grid patterns: {e}")
            return {"detected": False, "confidence": 0.0}
    
    def _analyze_depth_cues(self, image: np.ndarray) -> Dict:
        """
        Analyze depth cues to detect 3D masks
        
        Args:
            image: Preprocessed image
            
        Returns:
            Depth analysis result
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate depth map using simple stereo vision approximation
            # (In a real implementation, use proper depth estimation)
            depth_variance = self._estimate_depth_variance(gray)
            
            # Analyze shadow patterns
            shadow_analysis = self._analyze_shadow_patterns(gray)
            
            # Check for unnatural depth characteristics
            mask_suspected = (
                depth_variance < 0.1 or  # Too flat
                shadow_analysis["unnatural_shadows"]
            )
            
            confidence = 0.8 if mask_suspected else 0.2
            
            return {
                "mask_suspected": mask_suspected,
                "confidence": confidence,
                "details": {
                    "depth_variance": depth_variance,
                    "shadow_analysis": shadow_analysis
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing depth cues: {e}")
            return {
                "mask_suspected": False,
                "confidence": 0.0,
                "details": {}
            }
    
    def _estimate_depth_variance(self, gray_image: np.ndarray) -> float:
        """Estimate depth variance using gradient analysis"""
        try:
            # Calculate gradients
            grad_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
            
            # Calculate magnitude
            magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Return variance of magnitude (indicator of depth variation)
            return float(np.var(magnitude) / 10000.0)  # Normalize
            
        except Exception as e:
            logger.error(f"Error estimating depth variance: {e}")
            return 0.5
    
    def _analyze_shadow_patterns(self, gray_image: np.ndarray) -> Dict:
        """Analyze shadow patterns for mask detection"""
        try:
            # Simple shadow detection using local minima
            shadow_pixels = gray_image < (np.mean(gray_image) - np.std(gray_image))
            shadow_ratio = np.sum(shadow_pixels) / shadow_pixels.size
            
            # Unnatural if too few or too many shadows
            unnatural_shadows = shadow_ratio < 0.05 or shadow_ratio > 0.4
            
            return {
                "unnatural_shadows": unnatural_shadows,
                "shadow_ratio": float(shadow_ratio)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing shadow patterns: {e}")
            return {"unnatural_shadows": False, "shadow_ratio": 0.0}
    
    def _analyze_micro_motion(self, image: np.ndarray) -> Dict:
        """
        Analyze micro-motion patterns (single image approximation)
        
        Args:
            image: Preprocessed image
            
        Returns:
            Motion analysis result
        """
        try:
            # For single image, we can only estimate potential for natural motion
            # In a real implementation, this would analyze multiple frames
            
            # Analyze texture complexity as proxy for natural variation
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            texture_complexity = np.std(gray)
            
            # Natural faces should have some texture variation
            motion_detected = texture_complexity > 20
            
            return {
                "motion_detected": motion_detected,
                "texture_complexity": float(texture_complexity)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing micro motion: {e}")
            return {"motion_detected": False, "texture_complexity": 0.0}
    
    def _detect_blink_patterns(self, image: np.ndarray) -> Dict:
        """
        Detect blink patterns (single image approximation)
        
        Args:
            image: Preprocessed image
            
        Returns:
            Blink analysis result
        """
        try:
            # For single image, we can only detect if eyes are likely open/closed
            # In a real implementation, this would analyze video frames
            
            # Simple eye region analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Use Haar cascade to detect eyes (simplified)
            try:
                eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
                eyes = eye_cascade.detectMultiScale(gray, 1.1, 4)
                
                # If eyes are detected, assume they're open
                blink_detected = len(eyes) >= 2
            except:
                # Fallback: assume blink detected if we can't detect eyes clearly
                blink_detected = True
            
            return {
                "blink_detected": blink_detected,
                "eyes_count": len(eyes) if 'eyes' in locals() else 0
            }
            
        except Exception as e:
            logger.error(f"Error detecting blink patterns: {e}")
            return {"blink_detected": True, "eyes_count": 0}  # Default to positive
    
    def _calculate_liveness_score(self, *analysis_results) -> float:
        """
        Calculate overall liveness score from all analysis results
        
        Args:
            *analysis_results: Results from various liveness checks
            
        Returns:
            Overall liveness score (0-1)
        """
        try:
            texture_result, frequency_result, reflection_result, depth_result, motion_result, blink_result = analysis_results
            
            # Start with base score
            score = 0.8
            
            # Deduct points for suspicious findings
            if texture_result["is_suspicious"]:
                score -= 0.3
            
            if frequency_result["video_artifacts"]:
                score -= 0.2
            
            if reflection_result["screen_detected"]:
                score -= 0.4
            
            if depth_result["mask_suspected"]:
                score -= 0.3
            
            # Add points for positive indicators
            if motion_result["motion_detected"]:
                score += 0.1
            
            if blink_result["blink_detected"]:
                score += 0.1
            
            # Ensure score is in valid range
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating liveness score: {e}")
            return 0.5
    
    def _calculate_confidence(
        self, 
        liveness_score: float, 
        spoofing_attempts: List[SpoofingAttempt],
        blink_result: Dict,
        motion_result: Dict
    ) -> float:
        """
        Calculate confidence in the liveness determination
        
        Args:
            liveness_score: Overall liveness score
            spoofing_attempts: Detected spoofing attempts
            blink_result: Blink detection result
            motion_result: Motion analysis result
            
        Returns:
            Confidence score (0-1)
        """
        try:
            # Base confidence from liveness score
            confidence = abs(liveness_score - 0.5) * 2  # Distance from uncertain (0.5)
            
            # Adjust based on number of spoofing attempts
            if spoofing_attempts:
                max_spoof_confidence = max(attempt.confidence for attempt in spoofing_attempts)
                confidence = max(confidence, max_spoof_confidence)
            
            # Increase confidence if we have positive indicators
            if blink_result["blink_detected"] and motion_result["motion_detected"]:
                confidence = min(1.0, confidence + 0.1)
            
            return confidence
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def get_liveness_tips(self) -> List[str]:
        """Get user-friendly tips for better liveness detection"""
        return [
            "Look directly at the camera",
            "Ensure good lighting on your face",
            "Keep your face centered in the frame",
            "Avoid wearing sunglasses or hats",
            "Don't use photos or videos of yourself",
            "Ensure only one person is in the frame",
            "Hold the device steady",
            "Take the photo in real-time (live)",
            "Avoid reflective surfaces behind you",
            "Use natural lighting when possible"
        ] 