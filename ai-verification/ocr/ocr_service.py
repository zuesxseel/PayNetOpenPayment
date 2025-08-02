"""
OCR Service for text extraction and document parsing
"""
import cv2
import numpy as np
import pytesseract
import easyocr
import re
import time
from typing import Dict, List, Optional, Tuple
from loguru import logger

from ..models.schemas import OCRResult, ExtractedData, BoundingBox, Coordinates, DocumentType
from ..utils.image_utils import ImageProcessor
from ..config.settings import settings, SingaporeDocumentConfig


class OCRService:
    """OCR service for extracting text from identity documents"""
    
    def __init__(self):
        self.easyocr_reader = None
        self.singapore_config = SingaporeDocumentConfig()
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Initialize OCR engines"""
        try:
            if settings.ocr_engine in ["easyocr", "all"]:
                self.easyocr_reader = easyocr.Reader(settings.ocr_languages, gpu=False)
                logger.info("EasyOCR initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OCR engines: {e}")
    
    def extract_text_from_document(
        self, 
        image_base64: str, 
        document_type: DocumentType
    ) -> OCRResult:
        """
        Extract text from document image
        
        Args:
            image_base64: Base64 encoded image
            document_type: Type of document (NRIC, passport, etc.)
            
        Returns:
            OCR result with extracted data
        """
        start_time = time.time()
        
        try:
            # Convert image
            image = ImageProcessor.base64_to_opencv(image_base64)
            
            # Preprocess image
            processed_image = self._preprocess_document_image(image, document_type)
            
            # Extract text using configured engine
            if settings.ocr_engine == "tesseract":
                ocr_result = self._extract_with_tesseract(processed_image)
            elif settings.ocr_engine == "easyocr":
                ocr_result = self._extract_with_easyocr(processed_image)
            elif settings.ocr_engine == "paddleocr":
                ocr_result = self._extract_with_paddleocr(processed_image)
            else:
                # Try multiple engines and use best result
                ocr_result = self._extract_with_multiple_engines(processed_image)
            
            # Parse structured data based on document type
            extracted_data = self._parse_document_data(
                ocr_result["raw_text"], 
                ocr_result["bounding_boxes"], 
                document_type
            )
            
            processing_time = time.time() - start_time
            
            return OCRResult(
                success=True,
                confidence=ocr_result["confidence"],
                extracted_data=extracted_data,
                raw_text=ocr_result["raw_text"],
                bounding_boxes=ocr_result["bounding_boxes"],
                processing_time=processing_time,
                engine_used=settings.ocr_engine
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in OCR extraction: {e}")
            
            return OCRResult(
                success=False,
                confidence=0.0,
                extracted_data=ExtractedData(),
                raw_text="",
                bounding_boxes=[],
                processing_time=processing_time,
                engine_used=settings.ocr_engine
            )
    
    def _preprocess_document_image(
        self, 
        image: np.ndarray, 
        document_type: DocumentType
    ) -> np.ndarray:
        """
        Preprocess document image for OCR
        
        Args:
            image: OpenCV image
            document_type: Type of document
            
        Returns:
            Preprocessed image
        """
        # Detect and correct document perspective
        corners = ImageProcessor.detect_document_corners(image)
        if corners is not None:
            image = ImageProcessor.perspective_correction(image, corners)
        
        # Resize for optimal OCR
        image = ImageProcessor.resize_image(image, 1500, 1500)
        
        # Enhance image quality
        image = ImageProcessor.enhance_image_quality(image)
        
        # Document-specific preprocessing
        if document_type == DocumentType.NRIC:
            image = self._preprocess_nric(image)
        elif document_type == DocumentType.PASSPORT:
            image = self._preprocess_passport(image)
        elif document_type == DocumentType.DRIVING_LICENSE:
            image = self._preprocess_driving_license(image)
        
        return image
    
    def _preprocess_nric(self, image: np.ndarray) -> np.ndarray:
        """Preprocess NRIC image"""
        # NRIC-specific preprocessing
        # Apply bilateral filter to reduce noise while preserving edges
        filtered = cv2.bilateralFilter(image, 9, 75, 75)
        
        # Convert to grayscale
        gray = cv2.cvtColor(filtered, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive threshold
        adaptive_thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        return adaptive_thresh
    
    def _preprocess_passport(self, image: np.ndarray) -> np.ndarray:
        """Preprocess passport image"""
        # Focus on MRZ area (bottom part of passport)
        height, width = image.shape[:2]
        mrz_area = image[int(height * 0.8):, :]  # Bottom 20%
        
        # Apply OCR preprocessing
        processed = ImageProcessor.preprocess_for_ocr(mrz_area)
        
        return processed
    
    def _preprocess_driving_license(self, image: np.ndarray) -> np.ndarray:
        """Preprocess driving license image"""
        # Standard OCR preprocessing for driving license
        return ImageProcessor.preprocess_for_ocr(image)
    
    def _extract_with_tesseract(self, image: np.ndarray) -> Dict:
        """Extract text using Tesseract OCR"""
        try:
            # Configure Tesseract
            config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            
            # Extract text with bounding boxes
            data = pytesseract.image_to_data(
                image, 
                config=config, 
                output_type=pytesseract.Output.DICT
            )
            
            # Filter results by confidence
            raw_text = ""
            bounding_boxes = []
            confidences = []
            
            for i, conf in enumerate(data['conf']):
                if int(conf) > settings.ocr_confidence_threshold * 100:
                    text = data['text'][i].strip()
                    if text:
                        raw_text += text + " "
                        
                        # Create bounding box
                        bbox = BoundingBox(
                            coordinates=Coordinates(
                                x=float(data['left'][i]),
                                y=float(data['top'][i]),
                                width=float(data['width'][i]),
                                height=float(data['height'][i])
                            ),
                            confidence=float(conf) / 100.0,
                            text=text
                        )
                        bounding_boxes.append(bbox)
                        confidences.append(conf)
            
            avg_confidence = np.mean(confidences) / 100.0 if confidences else 0.0
            
            return {
                "raw_text": raw_text.strip(),
                "bounding_boxes": bounding_boxes,
                "confidence": avg_confidence
            }
            
        except Exception as e:
            logger.error(f"Tesseract OCR error: {e}")
            return {"raw_text": "", "bounding_boxes": [], "confidence": 0.0}
    
    def _extract_with_easyocr(self, image: np.ndarray) -> Dict:
        """Extract text using EasyOCR"""
        try:
            if self.easyocr_reader is None:
                raise Exception("EasyOCR not initialized")
            
            # Extract text
            results = self.easyocr_reader.readtext(image)
            
            raw_text = ""
            bounding_boxes = []
            confidences = []
            
            for (bbox_coords, text, confidence) in results:
                if confidence > settings.ocr_confidence_threshold:
                    raw_text += text + " "
                    
                    # Convert bbox coordinates
                    x_coords = [point[0] for point in bbox_coords]
                    y_coords = [point[1] for point in bbox_coords]
                    
                    bbox = BoundingBox(
                        coordinates=Coordinates(
                            x=float(min(x_coords)),
                            y=float(min(y_coords)),
                            width=float(max(x_coords) - min(x_coords)),
                            height=float(max(y_coords) - min(y_coords))
                        ),
                        confidence=float(confidence),
                        text=text
                    )
                    bounding_boxes.append(bbox)
                    confidences.append(confidence)
            
            avg_confidence = np.mean(confidences) if confidences else 0.0
            
            return {
                "raw_text": raw_text.strip(),
                "bounding_boxes": bounding_boxes,
                "confidence": avg_confidence
            }
            
        except Exception as e:
            logger.error(f"EasyOCR error: {e}")
            return {"raw_text": "", "bounding_boxes": [], "confidence": 0.0}
    
    def _extract_with_paddleocr(self, image: np.ndarray) -> Dict:
        """Extract text using PaddleOCR"""
        try:
            from paddleocr import PaddleOCR
            
            ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)
            results = ocr.ocr(image, cls=True)
            
            raw_text = ""
            bounding_boxes = []
            confidences = []
            
            for line in results:
                for word_info in line:
                    bbox_coords, (text, confidence) = word_info
                    
                    if confidence > settings.ocr_confidence_threshold:
                        raw_text += text + " "
                        
                        # Convert bbox coordinates
                        x_coords = [point[0] for point in bbox_coords]
                        y_coords = [point[1] for point in bbox_coords]
                        
                        bbox = BoundingBox(
                            coordinates=Coordinates(
                                x=float(min(x_coords)),
                                y=float(min(y_coords)),
                                width=float(max(x_coords) - min(x_coords)),
                                height=float(max(y_coords) - min(y_coords))
                            ),
                            confidence=float(confidence),
                            text=text
                        )
                        bounding_boxes.append(bbox)
                        confidences.append(confidence)
            
            avg_confidence = np.mean(confidences) if confidences else 0.0
            
            return {
                "raw_text": raw_text.strip(),
                "bounding_boxes": bounding_boxes,
                "confidence": avg_confidence
            }
            
        except Exception as e:
            logger.error(f"PaddleOCR error: {e}")
            return {"raw_text": "", "bounding_boxes": [], "confidence": 0.0}
    
    def _extract_with_multiple_engines(self, image: np.ndarray) -> Dict:
        """Extract text using multiple engines and return best result"""
        results = []
        
        # Try each engine
        engines = ["tesseract", "easyocr", "paddleocr"]
        for engine in engines:
            try:
                if engine == "tesseract":
                    result = self._extract_with_tesseract(image)
                elif engine == "easyocr":
                    result = self._extract_with_easyocr(image)
                elif engine == "paddleocr":
                    result = self._extract_with_paddleocr(image)
                
                result["engine"] = engine
                results.append(result)
                
            except Exception as e:
                logger.warning(f"Engine {engine} failed: {e}")
        
        # Return result with highest confidence
        if results:
            best_result = max(results, key=lambda x: x["confidence"])
            return best_result
        
        return {"raw_text": "", "bounding_boxes": [], "confidence": 0.0}
    
    def _parse_document_data(
        self, 
        raw_text: str, 
        bounding_boxes: List[BoundingBox], 
        document_type: DocumentType
    ) -> ExtractedData:
        """
        Parse structured data from raw OCR text
        
        Args:
            raw_text: Raw extracted text
            bounding_boxes: Text bounding boxes
            document_type: Type of document
            
        Returns:
            Structured extracted data
        """
        if document_type == DocumentType.NRIC:
            return self._parse_nric_data(raw_text, bounding_boxes)
        elif document_type == DocumentType.PASSPORT:
            return self._parse_passport_data(raw_text, bounding_boxes)
        elif document_type == DocumentType.DRIVING_LICENSE:
            return self._parse_driving_license_data(raw_text, bounding_boxes)
        else:
            return ExtractedData()
    
    def _parse_nric_data(self, raw_text: str, bounding_boxes: List[BoundingBox]) -> ExtractedData:
        """Parse NRIC specific data"""
        extracted_data = ExtractedData()
        
        # Clean text
        text = re.sub(r'[^\w\s]', ' ', raw_text).upper()
        
        # Extract NRIC number
        nric_pattern = self.singapore_config.NRIC_PATTERNS["format"]
        nric_match = re.search(nric_pattern, text)
        if nric_match:
            extracted_data.nric = nric_match.group()
        
        # Extract name (usually the longest text sequence)
        words = text.split()
        potential_names = []
        
        for i, word in enumerate(words):
            if word.isalpha() and len(word) > 2:
                # Look for consecutive alphabetic words
                name_parts = [word]
                j = i + 1
                while j < len(words) and words[j].isalpha() and len(words[j]) > 1:
                    name_parts.append(words[j])
                    j += 1
                
                if len(name_parts) >= 2:  # At least first and last name
                    potential_names.append(" ".join(name_parts))
        
        # Choose the longest name as it's likely the full name
        if potential_names:
            extracted_data.name = max(potential_names, key=len)
        
        # Extract date of birth (common patterns)
        dob_patterns = [
            r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{4})\b',
            r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b',
            r'\b(\d{1,2}\s\w{3}\s\d{4})\b'
        ]
        
        for pattern in dob_patterns:
            dob_match = re.search(pattern, raw_text)
            if dob_match:
                extracted_data.date_of_birth = dob_match.group(1)
                break
        
        # Extract gender
        if re.search(r'\bMALE\b', text):
            extracted_data.gender = "MALE"
        elif re.search(r'\bFEMALE\b', text):
            extracted_data.gender = "FEMALE"
        
        # Set nationality for Singapore NRIC
        extracted_data.nationality = "SINGAPORE"
        
        return extracted_data
    
    def _parse_passport_data(self, raw_text: str, bounding_boxes: List[BoundingBox]) -> ExtractedData:
        """Parse passport specific data"""
        extracted_data = ExtractedData()
        
        # Look for MRZ (Machine Readable Zone) data
        mrz_pattern = r'P<SGP([A-Z0-9<]+)'
        mrz_match = re.search(mrz_pattern, raw_text)
        
        if mrz_match:
            mrz_data = mrz_match.group(1)
            # Parse name from MRZ
            name_parts = mrz_data.split('<')
            if len(name_parts) >= 2:
                surname = name_parts[0].replace('<', ' ').strip()
                given_names = name_parts[1].replace('<', ' ').strip()
                extracted_data.name = f"{given_names} {surname}".strip()
        
        # Extract passport number
        passport_pattern = self.singapore_config.PASSPORT_PATTERNS["format"]
        passport_match = re.search(passport_pattern, raw_text)
        if passport_match:
            extracted_data.document_number = passport_match.group()
        
        # Set nationality
        extracted_data.nationality = "SINGAPORE"
        
        return extracted_data
    
    def _parse_driving_license_data(self, raw_text: str, bounding_boxes: List[BoundingBox]) -> ExtractedData:
        """Parse driving license specific data"""
        extracted_data = ExtractedData()
        
        # Extract license number (follows NRIC format in Singapore)
        license_pattern = self.singapore_config.DRIVING_LICENSE_PATTERNS["format"]
        license_match = re.search(license_pattern, raw_text)
        if license_match:
            extracted_data.document_number = license_match.group()
        
        # Extract name (similar to NRIC parsing)
        text = re.sub(r'[^\w\s]', ' ', raw_text).upper()
        words = text.split()
        
        for i, word in enumerate(words):
            if word.isalpha() and len(word) > 2:
                name_parts = [word]
                j = i + 1
                while j < len(words) and words[j].isalpha() and len(words[j]) > 1:
                    name_parts.append(words[j])
                    j += 1
                
                if len(name_parts) >= 2:
                    extracted_data.name = " ".join(name_parts)
                    break
        
        return extracted_data
    
    def validate_extracted_data(
        self, 
        extracted_data: ExtractedData, 
        document_type: DocumentType
    ) -> bool:
        """
        Validate extracted data against document format rules
        
        Args:
            extracted_data: Extracted document data
            document_type: Type of document
            
        Returns:
            True if data is valid
        """
        if document_type == DocumentType.NRIC:
            return self._validate_nric_data(extracted_data)
        elif document_type == DocumentType.PASSPORT:
            return self._validate_passport_data(extracted_data)
        elif document_type == DocumentType.DRIVING_LICENSE:
            return self._validate_driving_license_data(extracted_data)
        
        return False
    
    def _validate_nric_data(self, data: ExtractedData) -> bool:
        """Validate NRIC data"""
        if not data.nric:
            return False
        
        # Check NRIC format
        pattern = self.singapore_config.NRIC_PATTERNS["format"]
        if not re.match(pattern, data.nric):
            return False
        
        # Validate NRIC checksum
        return self._validate_nric_checksum(data.nric)
    
    def _validate_nric_checksum(self, nric: str) -> bool:
        """Validate NRIC checksum"""
        try:
            weights = self.singapore_config.NRIC_PATTERNS["checksum_weights"]
            digits = [int(d) for d in nric[1:8]]  # Extract 7 digits
            
            # Calculate weighted sum
            weighted_sum = sum(d * w for d, w in zip(digits, weights))
            
            # Determine checksum letter based on prefix and remainder
            remainder = weighted_sum % 11
            prefix = nric[0]
            
            if prefix in ['S', 'T']:
                checksum_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'Z', 'J']
            else:  # F, G
                checksum_letters = ['K', 'L', 'M', 'N', 'P', 'Q', 'R', 'T', 'U', 'W', 'X']
            
            expected_letter = checksum_letters[remainder]
            return nric[-1] == expected_letter
            
        except (ValueError, IndexError):
            return False
    
    def _validate_passport_data(self, data: ExtractedData) -> bool:
        """Validate passport data"""
        if not data.document_number:
            return False
        
        pattern = self.singapore_config.PASSPORT_PATTERNS["format"]
        return bool(re.match(pattern, data.document_number))
    
    def _validate_driving_license_data(self, data: ExtractedData) -> bool:
        """Validate driving license data"""
        if not data.document_number:
            return False
        
        pattern = self.singapore_config.DRIVING_LICENSE_PATTERNS["format"]
        return bool(re.match(pattern, data.document_number)) 