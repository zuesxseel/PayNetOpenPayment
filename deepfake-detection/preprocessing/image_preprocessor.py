"""
Image Preprocessing Module for Deepfake Detection
Handles image normalization, augmentation, and feature extraction
"""
import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from typing import List, Tuple, Optional, Dict, Any, Union
from PIL import Image
import mediapipe as mp
from loguru import logger
import albumentations as A
from albumentations.pytorch import ToTensorV2

from ..models.schemas import BoundingBox, FaceInfo
from ..config.settings import settings


class ImagePreprocessor:
    """Handles all image preprocessing tasks for deepfake detection"""
    
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        )
        
        # Standard transforms for deepfake detection models
        self.standard_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # Augmentation pipeline for training data
        self.augmentation_pipeline = A.Compose([
            A.RandomResizedCrop(224, 224, scale=(0.8, 1.0)),
            A.HorizontalFlip(p=0.5),
            A.OneOf([
                A.CLAHE(clip_limit=2),
                A.Sharpen(),
                A.Emboss(),
                A.RandomBrightnessContrast(),
            ], p=0.3),
            A.OneOf([
                A.GaussNoise(),
                A.GaussianBlur(blur_limit=(3, 7)),
                A.MotionBlur(blur_limit=7),
            ], p=0.2),
            A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=30, val_shift_limit=20, p=0.3),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2(),
        ])
        
        logger.info("Image Preprocessor initialized")
    
    def preprocess_image(
        self, 
        image: np.ndarray, 
        target_size: Tuple[int, int] = (224, 224),
        apply_augmentation: bool = False
    ) -> torch.Tensor:
        """
        Preprocess single image for deepfake detection
        
        Args:
            image: Input image as numpy array (H, W, C)
            target_size: Target size for resizing
            apply_augmentation: Whether to apply data augmentation
            
        Returns:
            Preprocessed image tensor
        """
        try:
            # Convert BGR to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            if apply_augmentation:
                # Apply augmentation pipeline
                augmented = self.augmentation_pipeline(image=image)
                return augmented['image']
            else:
                # Apply standard preprocessing
                pil_image = Image.fromarray(image)
                return self.standard_transform(pil_image)
                
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            # Return zero tensor as fallback
            return torch.zeros(3, target_size[0], target_size[1])
    
    def preprocess_image_batch(
        self, 
        images: List[np.ndarray],
        target_size: Tuple[int, int] = (224, 224),
        apply_augmentation: bool = False
    ) -> torch.Tensor:
        """
        Preprocess batch of images
        
        Args:
            images: List of input images
            target_size: Target size for resizing
            apply_augmentation: Whether to apply data augmentation
            
        Returns:
            Batch tensor of shape (N, C, H, W)
        """
        try:
            processed_images = []
            
            for image in images:
                processed = self.preprocess_image(image, target_size, apply_augmentation)
                processed_images.append(processed.unsqueeze(0))
            
            return torch.cat(processed_images, dim=0)
            
        except Exception as e:
            logger.error(f"Error preprocessing image batch: {e}")
            return torch.zeros(len(images), 3, target_size[0], target_size[1])
    
    def extract_faces(
        self, 
        image: np.ndarray,
        confidence_threshold: float = 0.5,
        margin: float = 0.2
    ) -> List[Dict[str, Any]]:
        """
        Extract faces from image with bounding boxes
        
        Args:
            image: Input image
            confidence_threshold: Minimum confidence for face detection
            margin: Additional margin around detected faces
            
        Returns:
            List of face dictionaries with image patches and metadata
        """
        try:
            # Convert to RGB for MediaPipe
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.face_detection.process(rgb_image)
            
            faces = []
            if results.detections:
                h, w, _ = image.shape
                
                for detection in results.detections:
                    if detection.score[0] < confidence_threshold:
                        continue
                    
                    # Get bounding box
                    bbox = detection.location_data.relative_bounding_box
                    
                    # Convert to absolute coordinates with margin
                    x = max(0, int((bbox.xmin - margin) * w))
                    y = max(0, int((bbox.ymin - margin) * h))
                    width = min(w - x, int((bbox.width + 2 * margin) * w))
                    height = min(h - y, int((bbox.height + 2 * margin) * h))
                    
                    # Extract face patch
                    face_patch = image[y:y+height, x:x+width]
                    
                    if face_patch.size > 0:
                        faces.append({
                            'image': face_patch,
                            'bbox': BoundingBox(x=x, y=y, width=width, height=height),
                            'confidence': float(detection.score[0]),
                            'landmarks': self._extract_landmarks(detection),
                            'quality_score': self._assess_face_quality(face_patch)
                        })
            
            return faces
            
        except Exception as e:
            logger.error(f"Error extracting faces: {e}")
            return []
    
    def preprocess_face_patch(
        self, 
        face_patch: np.ndarray,
        target_size: Tuple[int, int] = (224, 224),
        apply_enhancement: bool = True
    ) -> torch.Tensor:
        """
        Preprocess extracted face patch for deepfake detection
        
        Args:
            face_patch: Extracted face image
            target_size: Target size for the model
            apply_enhancement: Whether to apply image enhancement
            
        Returns:
            Preprocessed face tensor
        """
        try:
            if apply_enhancement:
                face_patch = self._enhance_face_image(face_patch)
            
            return self.preprocess_image(face_patch, target_size)
            
        except Exception as e:
            logger.error(f"Error preprocessing face patch: {e}")
            return torch.zeros(3, target_size[0], target_size[1])
    
    def normalize_image(
        self, 
        image: np.ndarray,
        method: str = 'standard'
    ) -> np.ndarray:
        """
        Normalize image using different methods
        
        Args:
            image: Input image
            method: Normalization method ('standard', 'minmax', 'zscore')
            
        Returns:
            Normalized image
        """
        try:
            if method == 'standard':
                # Convert to float and normalize to [0, 1]
                return image.astype(np.float32) / 255.0
            
            elif method == 'minmax':
                # Min-max normalization
                min_val = image.min()
                max_val = image.max()
                if max_val > min_val:
                    return (image - min_val) / (max_val - min_val)
                return image
            
            elif method == 'zscore':
                # Z-score normalization
                mean = image.mean()
                std = image.std()
                if std > 0:
                    return (image - mean) / std
                return image - mean
            
            else:
                logger.warning(f"Unknown normalization method: {method}")
                return image
                
        except Exception as e:
            logger.error(f"Error normalizing image: {e}")
            return image
    
    def resize_with_aspect_ratio(
        self, 
        image: np.ndarray,
        target_size: Tuple[int, int],
        interpolation: int = cv2.INTER_LINEAR
    ) -> np.ndarray:
        """
        Resize image while maintaining aspect ratio
        
        Args:
            image: Input image
            target_size: Target (width, height)
            interpolation: OpenCV interpolation method
            
        Returns:
            Resized image with padding if necessary
        """
        try:
            h, w = image.shape[:2]
            target_w, target_h = target_size
            
            # Calculate scaling factor
            scale = min(target_w / w, target_h / h)
            
            # Calculate new dimensions
            new_w = int(w * scale)
            new_h = int(h * scale)
            
            # Resize image
            resized = cv2.resize(image, (new_w, new_h), interpolation=interpolation)
            
            # Create padded image
            if len(image.shape) == 3:
                padded = np.zeros((target_h, target_w, image.shape[2]), dtype=image.dtype)
            else:
                padded = np.zeros((target_h, target_w), dtype=image.dtype)
            
            # Calculate padding
            pad_x = (target_w - new_w) // 2
            pad_y = (target_h - new_h) // 2
            
            # Place resized image in center
            padded[pad_y:pad_y+new_h, pad_x:pad_x+new_w] = resized
            
            return padded
            
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return image
    
    def extract_image_features(self, image: np.ndarray) -> Dict[str, float]:
        """
        Extract various image quality and statistical features
        
        Args:
            image: Input image
            
        Returns:
            Dictionary of extracted features
        """
        try:
            features = {}
            
            # Convert to grayscale for some calculations
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Brightness and contrast
            features['mean_brightness'] = float(gray.mean())
            features['std_brightness'] = float(gray.std())
            
            # Histogram features
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            features['hist_entropy'] = self._calculate_histogram_entropy(hist)
            
            # Edge density
            edges = cv2.Canny(gray, 50, 150)
            features['edge_density'] = float(edges.sum()) / (gray.shape[0] * gray.shape[1])
            
            # Laplacian variance (focus measure)
            features['laplacian_variance'] = float(cv2.Laplacian(gray, cv2.CV_64F).var())
            
            # Color features if image is colored
            if len(image.shape) == 3:
                b, g, r = cv2.split(image)
                features['color_variance'] = float(np.var([b.mean(), g.mean(), r.mean()]))
                
                # HSV features
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                h, s, v = cv2.split(hsv)
                features['saturation_mean'] = float(s.mean())
                features['hue_std'] = float(h.std())
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting image features: {e}")
            return {}
    
    def detect_compression_artifacts(self, image: np.ndarray) -> Dict[str, float]:
        """
        Detect JPEG compression artifacts that might indicate manipulation
        
        Args:
            image: Input image
            
        Returns:
            Dictionary of compression artifact metrics
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # DCT-based analysis for JPEG artifacts
            dct_coeffs = cv2.dct(gray.astype(np.float32))
            
            # High frequency energy
            h, w = gray.shape
            high_freq_energy = np.sum(np.abs(dct_coeffs[h//2:, w//2:]))
            total_energy = np.sum(np.abs(dct_coeffs))
            
            artifacts = {
                'high_freq_ratio': float(high_freq_energy / (total_energy + 1e-8)),
                'dct_sparsity': float(np.count_nonzero(np.abs(dct_coeffs) > 0.1) / (h * w)),
                'blocking_artifacts': self._detect_blocking_artifacts(gray)
            }
            
            return artifacts
            
        except Exception as e:
            logger.error(f"Error detecting compression artifacts: {e}")
            return {}
    
    def _enhance_face_image(self, face_patch: np.ndarray) -> np.ndarray:
        """Apply image enhancement techniques to face patch"""
        try:
            # Apply CLAHE for contrast enhancement
            if len(face_patch.shape) == 3:
                lab = cv2.cvtColor(face_patch, cv2.COLOR_BGR2LAB)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                lab[:, :, 0] = clahe.apply(lab[:, :, 0])
                enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            else:
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                enhanced = clahe.apply(face_patch)
            
            # Mild sharpening
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            sharpened = cv2.filter2D(enhanced, -1, kernel * 0.1 + np.eye(3) * 0.9)
            
            return sharpened
            
        except Exception as e:
            logger.error(f"Error enhancing face image: {e}")
            return face_patch
    
    def _extract_landmarks(self, detection) -> Optional[List[Tuple[float, float]]]:
        """Extract facial landmarks from MediaPipe detection"""
        try:
            if hasattr(detection, 'location_data') and hasattr(detection.location_data, 'relative_keypoints'):
                landmarks = []
                for keypoint in detection.location_data.relative_keypoints:
                    landmarks.append((float(keypoint.x), float(keypoint.y)))
                return landmarks
            return None
        except Exception:
            return None
    
    def _assess_face_quality(self, face_patch: np.ndarray) -> float:
        """Assess the quality of extracted face patch"""
        try:
            gray = cv2.cvtColor(face_patch, cv2.COLOR_BGR2GRAY) if len(face_patch.shape) == 3 else face_patch
            
            # Sharpness measure using Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Brightness check
            brightness = gray.mean()
            brightness_score = 1.0 - abs(brightness - 128) / 128
            
            # Size check
            size_score = min(face_patch.shape[0] * face_patch.shape[1] / (100 * 100), 1.0)
            
            # Combined quality score
            quality = (laplacian_var / 1000 + brightness_score + size_score) / 3
            return min(quality, 1.0)
            
        except Exception:
            return 0.5
    
    def _calculate_histogram_entropy(self, hist: np.ndarray) -> float:
        """Calculate entropy of histogram"""
        try:
            # Normalize histogram
            hist_norm = hist / (hist.sum() + 1e-8)
            # Remove zero bins
            hist_norm = hist_norm[hist_norm > 0]
            # Calculate entropy
            entropy = -np.sum(hist_norm * np.log2(hist_norm + 1e-8))
            return float(entropy)
        except Exception:
            return 0.0
    
    def _detect_blocking_artifacts(self, gray: np.ndarray) -> float:
        """Detect JPEG blocking artifacts"""
        try:
            # Look for 8x8 blocking patterns typical of JPEG
            h, w = gray.shape
            
            # Calculate differences at 8-pixel intervals
            block_diffs_h = []
            block_diffs_v = []
            
            for i in range(8, h, 8):
                if i < h - 1:
                    diff = np.mean(np.abs(gray[i, :] - gray[i-1, :]))
                    block_diffs_h.append(diff)
            
            for j in range(8, w, 8):
                if j < w - 1:
                    diff = np.mean(np.abs(gray[:, j] - gray[:, j-1]))
                    block_diffs_v.append(diff)
            
            if block_diffs_h and block_diffs_v:
                return float(np.mean(block_diffs_h + block_diffs_v))
            
            return 0.0
            
        except Exception:
            return 0.0 