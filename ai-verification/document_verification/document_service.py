"""
Document Verification Service for authenticity and security feature checks
"""
import cv2
import numpy as np
import time
from typing import List, Dict, Optional
from loguru import logger

from ..models.schemas import (
    DocumentVerificationResult, SecurityFeature, SecurityFeatureType, 
    DocumentType, BoundingBox, Coordinates
)
from ..utils.image_utils import ImageProcessor
from ..config.settings import settings, SingaporeDocumentConfig, ThresholdConfig


class DocumentVerificationService:
    """Document verification service for authenticity checks"""
    
    def __init__(self):
        self.singapore_config = SingaporeDocumentConfig()
        self._load_templates()
    
    def _load_templates(self):
        """Load document templates for comparison"""
        try:
            # In a real implementation, load actual document templates
            # For now, create placeholder templates
            self.templates = {
                DocumentType.NRIC: {"template": "nric_template", "features": ["hologram", "microtext", "rfid"]},
                DocumentType.PASSPORT: {"template": "passport_template", "features": ["hologram", "watermark", "rfid"]},
                DocumentType.DRIVING_LICENSE: {"template": "dl_template", "features": ["hologram", "barcode"]}
            }
            logger.info("Document templates loaded successfully")
        except Exception as e:
            logger.error(f"Error loading document templates: {e}")
    
    def verify_document_authenticity(
        self, 
        image_base64: str, 
        document_type: DocumentType
    ) -> DocumentVerificationResult:
        """
        Verify document authenticity and security features
        
        Args:
            image_base64: Base64 encoded document image
            document_type: Type of document to verify
            
        Returns:
            Document verification result
        """
        start_time = time.time()
        
        try:
            # Convert image
            image = ImageProcessor.base64_to_opencv(image_base64)
            
            # Preprocess for document analysis
            processed_image = self._preprocess_document(image, document_type)
            
            # Check security features
            security_features = self._check_security_features(processed_image, document_type)
            
            # Perform template matching
            template_score = self._perform_template_matching(processed_image, document_type)
            
            # Check for tampering
            tampering_detected = self._detect_tampering(processed_image)
            
            # Calculate overall authenticity score
            authenticity_score = self._calculate_authenticity_score(
                security_features, template_score, tampering_detected
            )
            
            # Determine if document is authentic
            is_authentic = (
                authenticity_score >= ThresholdConfig.DOCUMENT_AUTHENTICITY and
                not tampering_detected and
                template_score >= ThresholdConfig.TEMPLATE_MATCH_THRESHOLD
            )
            
            processing_time = time.time() - start_time
            
            return DocumentVerificationResult(
                success=True,
                is_authentic=is_authentic,
                confidence=authenticity_score,
                document_type=document_type,
                issuer=self._get_document_issuer(document_type),
                security_features=security_features,
                template_match_score=template_score,
                tampering_detected=tampering_detected,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in document verification: {e}")
            
            return DocumentVerificationResult(
                success=False,
                is_authentic=False,
                confidence=0.0,
                document_type=document_type,
                issuer="Unknown",
                security_features=[],
                template_match_score=0.0,
                tampering_detected=True,
                processing_time=processing_time
            )
    
    def _preprocess_document(self, image: np.ndarray, document_type: DocumentType) -> np.ndarray:
        """Preprocess document image for verification"""
        # Detect document corners and apply perspective correction
        corners = ImageProcessor.detect_document_corners(image)
        if corners is not None:
            image = ImageProcessor.perspective_correction(image, corners)
        
        # Resize to standard size
        image = ImageProcessor.resize_image(image, 800, 600)
        
        # Enhance image quality
        image = ImageProcessor.enhance_image_quality(image)
        
        return image
    
    def _check_security_features(
        self, 
        image: np.ndarray, 
        document_type: DocumentType
    ) -> List[SecurityFeature]:
        """Check for security features in document"""
        security_features = []
        
        # Get expected features for document type
        expected_features = self.singapore_config.SECURITY_FEATURES.get(
            document_type.value, []
        )
        
        for feature_type in expected_features:
            feature_result = self._detect_security_feature(image, feature_type)
            
            security_features.append(SecurityFeature(
                type=SecurityFeatureType(feature_type),
                present=feature_result["present"],
                valid=feature_result["valid"],
                confidence=feature_result["confidence"],
                location=feature_result.get("location")
            ))
        
        return security_features
    
    def _detect_security_feature(self, image: np.ndarray, feature_type: str) -> Dict:
        """Detect specific security feature"""
        try:
            if feature_type == "hologram":
                return self._detect_hologram(image)
            elif feature_type == "watermark":
                return self._detect_watermark(image)
            elif feature_type == "microtext":
                return self._detect_microtext(image)
            elif feature_type == "rfid":
                return self._detect_rfid_chip(image)
            elif feature_type == "barcode":
                return self._detect_barcode(image)
            elif feature_type == "magnetic_stripe":
                return self._detect_magnetic_stripe(image)
            else:
                return {"present": False, "valid": False, "confidence": 0.0}
                
        except Exception as e:
            logger.error(f"Error detecting security feature {feature_type}: {e}")
            return {"present": False, "valid": False, "confidence": 0.0}
    
    def _detect_hologram(self, image: np.ndarray) -> Dict:
        """Detect holographic security features"""
        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Look for iridescent colors typical of holograms
            # Holograms often show rainbow-like color variations
            hue_channel = hsv[:, :, 0]
            
            # Calculate hue variance (holograms have high color variation)
            hue_variance = np.var(hue_channel)
            
            # Look for metallic/reflective regions
            value_channel = hsv[:, :, 2]
            bright_regions = value_channel > 200
            metallic_ratio = np.sum(bright_regions) / bright_regions.size
            
            # Simple hologram detection based on color variation and reflectivity
            hologram_score = min(1.0, (hue_variance / 1000.0) + (metallic_ratio * 2))
            
            present = hologram_score > 0.3
            valid = hologram_score > 0.6
            
            return {
                "present": present,
                "valid": valid,
                "confidence": hologram_score
            }
            
        except Exception as e:
            logger.error(f"Error detecting hologram: {e}")
            return {"present": False, "valid": False, "confidence": 0.0}
    
    def _detect_watermark(self, image: np.ndarray) -> Dict:
        """Detect watermark security features"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply different lighting conditions to reveal watermarks
            # Watermarks are often visible under backlighting
            
            # Enhance contrast to reveal subtle patterns
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Look for subtle patterns that might indicate watermarks
            # Using Laplacian to detect fine details
            laplacian = cv2.Laplacian(enhanced, cv2.CV_64F)
            detail_variance = np.var(laplacian)
            
            # Watermarks typically show as subtle variations
            watermark_score = min(1.0, detail_variance / 5000.0)
            
            present = watermark_score > 0.2
            valid = watermark_score > 0.4
            
            return {
                "present": present,
                "valid": valid,
                "confidence": watermark_score
            }
            
        except Exception as e:
            logger.error(f"Error detecting watermark: {e}")
            return {"present": False, "valid": False, "confidence": 0.0}
    
    def _detect_microtext(self, image: np.ndarray) -> Dict:
        """Detect microtext security features"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Enhance image to reveal fine text
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            sharpened = cv2.filter2D(gray, -1, kernel)
            
            # Look for very fine text patterns
            # Microtext appears as regular, very small patterns
            
            # Use morphological operations to detect text-like structures
            kernel_text = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
            morphed = cv2.morphologyEx(sharpened, cv2.MORPH_CLOSE, kernel_text)
            
            # Calculate difference to find text regions
            text_regions = cv2.absdiff(sharpened, morphed)
            text_score = np.mean(text_regions) / 255.0
            
            present = text_score > 0.1
            valid = text_score > 0.2
            
            return {
                "present": present,
                "valid": valid,
                "confidence": text_score
            }
            
        except Exception as e:
            logger.error(f"Error detecting microtext: {e}")
            return {"present": False, "valid": False, "confidence": 0.0}
    
    def _detect_rfid_chip(self, image: np.ndarray) -> Dict:
        """Detect RFID chip presence (visual detection only)"""
        try:
            # RFID chips often appear as small rectangular regions
            # with slightly different coloration or thickness
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Look for rectangular regions that might be chips
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            chip_candidates = 0
            for contour in contours:
                # Check if contour could be a chip
                area = cv2.contourArea(contour)
                if 100 < area < 1000:  # Reasonable chip size
                    # Check if roughly rectangular
                    approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
                    if len(approx) == 4:  # Rectangular
                        chip_candidates += 1
            
            # Simple scoring based on number of candidates
            chip_score = min(1.0, chip_candidates / 3.0)
            
            present = chip_score > 0.3
            valid = chip_score > 0.6
            
            return {
                "present": present,
                "valid": valid,
                "confidence": chip_score
            }
            
        except Exception as e:
            logger.error(f"Error detecting RFID chip: {e}")
            return {"present": False, "valid": False, "confidence": 0.0}
    
    def _detect_barcode(self, image: np.ndarray) -> Dict:
        """Detect barcode presence"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Look for barcode patterns - parallel lines
            # Apply morphological operations to enhance line patterns
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
            morphed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            
            # Calculate difference to find line patterns
            diff = cv2.absdiff(gray, morphed)
            
            # Look for regions with regular line patterns
            line_strength = np.mean(diff)
            
            # Use Hough lines to detect parallel lines
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=50)
            
            line_count = len(lines) if lines is not None else 0
            
            # Combine line strength and count
            barcode_score = min(1.0, (line_strength / 50.0) + (line_count / 20.0))
            
            present = barcode_score > 0.3
            valid = barcode_score > 0.6
            
            return {
                "present": present,
                "valid": valid,
                "confidence": barcode_score
            }
            
        except Exception as e:
            logger.error(f"Error detecting barcode: {e}")
            return {"present": False, "valid": False, "confidence": 0.0}
    
    def _detect_magnetic_stripe(self, image: np.ndarray) -> Dict:
        """Detect magnetic stripe presence"""
        try:
            # Magnetic stripes appear as dark horizontal bands
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Look for horizontal dark regions
            # Calculate horizontal gradients
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            
            # Look for regions with low horizontal variation (uniform strips)
            horizontal_variance = np.var(grad_x, axis=1)  # Variance along rows
            
            # Find rows with low variance (potential magnetic stripe)
            stripe_rows = horizontal_variance < np.percentile(horizontal_variance, 25)
            stripe_ratio = np.sum(stripe_rows) / len(stripe_rows)
            
            present = stripe_ratio > 0.1
            valid = stripe_ratio > 0.2
            
            return {
                "present": present,
                "valid": valid,
                "confidence": stripe_ratio
            }
            
        except Exception as e:
            logger.error(f"Error detecting magnetic stripe: {e}")
            return {"present": False, "valid": False, "confidence": 0.0}
    
    def _perform_template_matching(self, image: np.ndarray, document_type: DocumentType) -> float:
        """Perform template matching against known document layouts"""
        try:
            # In a real implementation, this would match against actual templates
            # For now, simulate template matching
            
            # Calculate image characteristics
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Analyze document layout using edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Calculate layout score based on edge distribution
            edge_density = np.sum(edges > 0) / edges.size
            
            # Simulate template matching score
            # Real implementation would compare with actual document templates
            if document_type == DocumentType.NRIC:
                base_score = 0.8
            elif document_type == DocumentType.PASSPORT:
                base_score = 0.7
            elif document_type == DocumentType.DRIVING_LICENSE:
                base_score = 0.75
            else:
                base_score = 0.5
            
            # Adjust based on edge density (good documents have consistent layouts)
            template_score = base_score * (0.5 + edge_density)
            
            return min(1.0, template_score)
            
        except Exception as e:
            logger.error(f"Error in template matching: {e}")
            return 0.0
    
    def _detect_tampering(self, image: np.ndarray) -> bool:
        """Detect signs of document tampering"""
        try:
            # Look for signs of digital or physical tampering
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Check for inconsistent compression artifacts
            compression_artifacts = self._detect_compression_artifacts(image)
            
            # Check for copy-paste artifacts
            copypaste_artifacts = self._detect_copypaste_artifacts(gray)
            
            # Check for inconsistent lighting
            lighting_inconsistency = self._detect_lighting_inconsistency(gray)
            
            # Document is considered tampered if any artifacts are detected
            tampering_detected = (
                compression_artifacts or 
                copypaste_artifacts or 
                lighting_inconsistency
            )
            
            return tampering_detected
            
        except Exception as e:
            logger.error(f"Error detecting tampering: {e}")
            return True  # Assume tampering if error occurs
    
    def _detect_compression_artifacts(self, image: np.ndarray) -> bool:
        """Detect inconsistent compression artifacts"""
        try:
            # Convert to YUV to analyze compression
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            
            # Analyze 8x8 blocks (typical JPEG compression)
            y_channel = yuv[:, :, 0]
            h, w = y_channel.shape
            
            block_variances = []
            for i in range(0, h-8, 8):
                for j in range(0, w-8, 8):
                    block = y_channel[i:i+8, j:j+8]
                    block_variances.append(np.var(block))
            
            # Inconsistent compression shows high variance in block variances
            variance_of_variances = np.var(block_variances)
            
            return variance_of_variances > 1000  # Threshold for artifact detection
            
        except Exception as e:
            logger.error(f"Error detecting compression artifacts: {e}")
            return False
    
    def _detect_copypaste_artifacts(self, gray_image: np.ndarray) -> bool:
        """Detect copy-paste tampering artifacts"""
        try:
            # Look for duplicated regions using template matching
            h, w = gray_image.shape
            
            # Sample small regions and check for duplicates
            template_size = 20
            matches_found = 0
            
            for i in range(0, h-template_size, template_size):
                for j in range(0, w-template_size, template_size):
                    template = gray_image[i:i+template_size, j:j+template_size]
                    
                    # Match template against rest of image
                    result = cv2.matchTemplate(gray_image, template, cv2.TM_CCOEFF_NORMED)
                    
                    # Count high-confidence matches (excluding the template location itself)
                    matches = np.where(result > 0.9)
                    if len(matches[0]) > 1:  # More than just the original location
                        matches_found += 1
            
            # Too many duplicate regions suggests copy-paste tampering
            return matches_found > 5
            
        except Exception as e:
            logger.error(f"Error detecting copy-paste artifacts: {e}")
            return False
    
    def _detect_lighting_inconsistency(self, gray_image: np.ndarray) -> bool:
        """Detect inconsistent lighting patterns"""
        try:
            # Analyze lighting gradients across the image
            # Consistent documents should have consistent lighting
            
            # Calculate gradients
            grad_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
            
            # Calculate magnitude
            magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Divide image into regions and analyze lighting consistency
            h, w = gray_image.shape
            region_size = min(h, w) // 4
            
            region_brightnesses = []
            for i in range(0, h-region_size, region_size):
                for j in range(0, w-region_size, region_size):
                    region = gray_image[i:i+region_size, j:j+region_size]
                    region_brightnesses.append(np.mean(region))
            
            # Check for inconsistent lighting
            brightness_variance = np.var(region_brightnesses)
            
            return brightness_variance > 500  # Threshold for lighting inconsistency
            
        except Exception as e:
            logger.error(f"Error detecting lighting inconsistency: {e}")
            return False
    
    def _calculate_authenticity_score(
        self, 
        security_features: List[SecurityFeature],
        template_score: float,
        tampering_detected: bool
    ) -> float:
        """Calculate overall document authenticity score"""
        try:
            # Start with template matching score
            score = template_score
            
            # Add security features score
            if security_features:
                valid_features = sum(1 for feature in security_features if feature.valid)
                total_features = len(security_features)
                feature_score = valid_features / total_features
                
                # Weight security features
                score = (score * 0.6) + (feature_score * 0.4)
            
            # Heavy penalty for tampering
            if tampering_detected:
                score *= 0.3
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating authenticity score: {e}")
            return 0.0
    
    def _get_document_issuer(self, document_type: DocumentType) -> str:
        """Get the issuing authority for document type"""
        issuers = {
            DocumentType.NRIC: "Immigration & Checkpoints Authority (ICA)",
            DocumentType.PASSPORT: "Immigration & Checkpoints Authority (ICA)",
            DocumentType.DRIVING_LICENSE: "Singapore Police Force (SPF)"
        }
        
        return issuers.get(document_type, "Unknown Authority") 