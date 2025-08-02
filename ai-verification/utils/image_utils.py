"""
Image processing utilities for AI verification
"""
import cv2
import numpy as np
import base64
import io
from PIL import Image, ImageEnhance, ImageFilter
from typing import Tuple, Optional, List
import magic
from loguru import logger


class ImageProcessor:
    """Image processing utilities"""
    
    @staticmethod
    def base64_to_opencv(base64_string: str) -> np.ndarray:
        """
        Convert base64 string to OpenCV image
        
        Args:
            base64_string: Base64 encoded image
            
        Returns:
            OpenCV image array
        """
        try:
            # Remove data URL prefix if present
            if "," in base64_string:
                base64_string = base64_string.split(",")[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_string)
            
            # Convert to numpy array
            np_array = np.frombuffer(image_data, np.uint8)
            
            # Decode as image
            image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image from base64")
                
            return image
            
        except Exception as e:
            logger.error(f"Error converting base64 to OpenCV: {e}")
            raise
    
    @staticmethod
    def opencv_to_base64(image: np.ndarray, format: str = "jpg") -> str:
        """
        Convert OpenCV image to base64 string
        
        Args:
            image: OpenCV image array
            format: Image format (jpg, png)
            
        Returns:
            Base64 encoded image string
        """
        try:
            # Encode image
            _, buffer = cv2.imencode(f'.{format}', image)
            
            # Convert to base64
            base64_string = base64.b64encode(buffer).decode('utf-8')
            
            return base64_string
            
        except Exception as e:
            logger.error(f"Error converting OpenCV to base64: {e}")
            raise
    
    @staticmethod
    def base64_to_pil(base64_string: str) -> Image.Image:
        """
        Convert base64 string to PIL Image
        
        Args:
            base64_string: Base64 encoded image
            
        Returns:
            PIL Image object
        """
        try:
            # Remove data URL prefix if present
            if "," in base64_string:
                base64_string = base64_string.split(",")[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_string)
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            return image
            
        except Exception as e:
            logger.error(f"Error converting base64 to PIL: {e}")
            raise
    
    @staticmethod
    def pil_to_base64(image: Image.Image, format: str = "JPEG") -> str:
        """
        Convert PIL Image to base64 string
        
        Args:
            image: PIL Image object
            format: Image format (JPEG, PNG)
            
        Returns:
            Base64 encoded image string
        """
        try:
            buffer = io.BytesIO()
            image.save(buffer, format=format)
            
            # Convert to base64
            base64_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return base64_string
            
        except Exception as e:
            logger.error(f"Error converting PIL to base64: {e}")
            raise
    
    @staticmethod
    def validate_image(base64_string: str) -> dict:
        """
        Validate image format and properties
        
        Args:
            base64_string: Base64 encoded image
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Remove data URL prefix if present
            if "," in base64_string:
                base64_string = base64_string.split(",")[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_string)
            
            # Check file type
            file_type = magic.from_buffer(image_data, mime=True)
            
            # Get image properties
            image = Image.open(io.BytesIO(image_data))
            
            return {
                "valid": True,
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "mime_type": file_type,
                "file_size": len(image_data)
            }
            
        except Exception as e:
            logger.error(f"Error validating image: {e}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    @staticmethod
    def resize_image(image: np.ndarray, max_width: int = 1024, max_height: int = 1024) -> np.ndarray:
        """
        Resize image while maintaining aspect ratio
        
        Args:
            image: OpenCV image array
            max_width: Maximum width
            max_height: Maximum height
            
        Returns:
            Resized image
        """
        height, width = image.shape[:2]
        
        # Calculate scaling factor
        scale = min(max_width / width, max_height / height)
        
        if scale < 1.0:
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        return image
    
    @staticmethod
    def enhance_image_quality(image: np.ndarray) -> np.ndarray:
        """
        Enhance image quality for better OCR/recognition
        
        Args:
            image: OpenCV image array
            
        Returns:
            Enhanced image
        """
        # Convert to PIL for enhancement
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(1.2)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(pil_image)
        pil_image = enhancer.enhance(1.1)
        
        # Apply unsharp mask
        pil_image = pil_image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
        
        # Convert back to OpenCV
        enhanced_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return enhanced_image
    
    @staticmethod
    def preprocess_for_ocr(image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for OCR
        
        Args:
            image: OpenCV image array
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply Gaussian blur to remove noise
        blurred = cv2.GaussianBlur(gray, (1, 1), 0)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations to clean up the image
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return processed
    
    @staticmethod
    def preprocess_for_face_recognition(image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for face recognition
        
        Args:
            image: OpenCV image array
            
        Returns:
            Preprocessed image
        """
        # Resize for consistent processing
        image = ImageProcessor.resize_image(image, 512, 512)
        
        # Enhance quality
        image = ImageProcessor.enhance_image_quality(image)
        
        # Apply histogram equalization for better lighting
        if len(image.shape) == 3:
            # Convert to YUV
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            # Equalize the Y channel
            yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])
            # Convert back to BGR
            image = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            image = cv2.equalizeHist(image)
        
        return image
    
    @staticmethod
    def detect_document_corners(image: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect document corners for perspective correction
        
        Args:
            image: OpenCV image array
            
        Returns:
            Document corners or None if not found
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Edge detection
            edges = cv2.Canny(blurred, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Sort contours by area
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            
            # Find the largest rectangular contour
            for contour in contours[:5]:
                # Approximate contour
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # If we have 4 points, it might be a document
                if len(approx) == 4:
                    return approx.reshape(4, 2)
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting document corners: {e}")
            return None
    
    @staticmethod
    def perspective_correction(image: np.ndarray, corners: np.ndarray) -> np.ndarray:
        """
        Apply perspective correction to document image
        
        Args:
            image: OpenCV image array
            corners: Document corners
            
        Returns:
            Perspective corrected image
        """
        try:
            # Order corners: top-left, top-right, bottom-right, bottom-left
            corners = ImageProcessor._order_corners(corners)
            
            # Calculate the width and height of the new image
            width_a = np.sqrt(((corners[2][0] - corners[3][0]) ** 2) + ((corners[2][1] - corners[3][1]) ** 2))
            width_b = np.sqrt(((corners[1][0] - corners[0][0]) ** 2) + ((corners[1][1] - corners[0][1]) ** 2))
            max_width = max(int(width_a), int(width_b))
            
            height_a = np.sqrt(((corners[1][0] - corners[2][0]) ** 2) + ((corners[1][1] - corners[2][1]) ** 2))
            height_b = np.sqrt(((corners[0][0] - corners[3][0]) ** 2) + ((corners[0][1] - corners[3][1]) ** 2))
            max_height = max(int(height_a), int(height_b))
            
            # Define destination points
            destination = np.array([
                [0, 0],
                [max_width - 1, 0],
                [max_width - 1, max_height - 1],
                [0, max_height - 1]
            ], dtype="float32")
            
            # Calculate perspective transform matrix
            matrix = cv2.getPerspectiveTransform(corners.astype("float32"), destination)
            
            # Apply perspective transformation
            warped = cv2.warpPerspective(image, matrix, (max_width, max_height))
            
            return warped
            
        except Exception as e:
            logger.error(f"Error applying perspective correction: {e}")
            return image
    
    @staticmethod
    def _order_corners(corners: np.ndarray) -> np.ndarray:
        """
        Order corners in clockwise order starting from top-left
        
        Args:
            corners: Array of corner points
            
        Returns:
            Ordered corners
        """
        # Calculate center point
        center = np.mean(corners, axis=0)
        
        # Calculate angles from center
        angles = np.arctan2(corners[:, 1] - center[1], corners[:, 0] - center[0])
        
        # Sort by angle
        sorted_indices = np.argsort(angles)
        
        # Reorder corners
        ordered_corners = corners[sorted_indices]
        
        return ordered_corners
    
    @staticmethod
    def calculate_image_quality(image: np.ndarray) -> dict:
        """
        Calculate various image quality metrics
        
        Args:
            image: OpenCV image array
            
        Returns:
            Dictionary with quality metrics
        """
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Calculate brightness
            brightness = np.mean(gray)
            
            # Calculate contrast (standard deviation)
            contrast = np.std(gray)
            
            # Calculate sharpness (Laplacian variance)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Calculate noise level
            noise = ImageProcessor._calculate_noise(gray)
            
            return {
                "brightness": float(brightness),
                "contrast": float(contrast),
                "sharpness": float(sharpness),
                "noise": float(noise),
                "resolution": gray.shape
            }
            
        except Exception as e:
            logger.error(f"Error calculating image quality: {e}")
            return {}
    
    @staticmethod
    def _calculate_noise(image: np.ndarray) -> float:
        """
        Calculate noise level in image
        
        Args:
            image: Grayscale image
            
        Returns:
            Noise level
        """
        # Use Laplacian to detect edges
        laplacian = cv2.Laplacian(image, cv2.CV_64F)
        
        # Calculate noise as variance of Laplacian
        noise = laplacian.var()
        
        return noise 