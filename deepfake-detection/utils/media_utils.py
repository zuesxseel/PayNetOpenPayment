"""
Media processing utilities for deepfake detection
"""
import cv2
import numpy as np
import base64
import io
import tempfile
import os
from PIL import Image
from typing import Tuple, Optional, List, Dict, Any, Generator
import magic
from loguru import logger
import librosa
import imageio
from moviepy.editor import VideoFileClip
import hashlib


class MediaProcessor:
    """Media processing utilities for deepfake detection"""
    
    @staticmethod
    def base64_to_bytes(base64_string: str) -> bytes:
        """Convert base64 string to bytes"""
        try:
            if "," in base64_string:
                base64_string = base64_string.split(",")[1]
            return base64.b64decode(base64_string)
        except Exception as e:
            logger.error(f"Error converting base64 to bytes: {e}")
            raise
    
    @staticmethod
    def bytes_to_base64(data: bytes) -> str:
        """Convert bytes to base64 string"""
        try:
            return base64.b64encode(data).decode('utf-8')
        except Exception as e:
            logger.error(f"Error converting bytes to base64: {e}")
            raise
    
    @staticmethod
    def validate_media(base64_string: str) -> Dict[str, Any]:
        """
        Validate media format and extract information
        
        Args:
            base64_string: Base64 encoded media
            
        Returns:
            Dictionary with validation results and media info
        """
        try:
            media_data = MediaProcessor.base64_to_bytes(base64_string)
            
            # Check file type
            file_type = magic.from_buffer(media_data, mime=True)
            
            # Create temporary file for analysis
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(media_data)
                temp_path = temp_file.name
            
            try:
                media_info = {
                    "valid": True,
                    "mime_type": file_type,
                    "file_size": len(media_data),
                    "file_path": temp_path
                }
                
                # Extract media-specific information
                if file_type.startswith('image/'):
                    image_info = MediaProcessor._get_image_info(temp_path)
                    media_info.update(image_info)
                    media_info["media_type"] = "image"
                    
                elif file_type.startswith('video/'):
                    video_info = MediaProcessor._get_video_info(temp_path)
                    media_info.update(video_info)
                    media_info["media_type"] = "video"
                    
                elif file_type.startswith('audio/'):
                    audio_info = MediaProcessor._get_audio_info(temp_path)
                    media_info.update(audio_info)
                    media_info["media_type"] = "audio"
                    
                else:
                    media_info["valid"] = False
                    media_info["error"] = f"Unsupported media type: {file_type}"
                
                return media_info
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Error validating media: {e}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    @staticmethod
    def _get_image_info(file_path: str) -> Dict[str, Any]:
        """Get image information"""
        try:
            with Image.open(file_path) as img:
                return {
                    "format": img.format,
                    "mode": img.mode,
                    "resolution": f"{img.width}x{img.height}",
                    "width": img.width,
                    "height": img.height
                }
        except Exception as e:
            logger.error(f"Error getting image info: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def _get_video_info(file_path: str) -> Dict[str, Any]:
        """Get video information"""
        try:
            with VideoFileClip(file_path) as clip:
                return {
                    "duration": clip.duration,
                    "fps": clip.fps,
                    "resolution": f"{clip.w}x{clip.h}",
                    "width": clip.w,
                    "height": clip.h,
                    "has_audio": clip.audio is not None
                }
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def _get_audio_info(file_path: str) -> Dict[str, Any]:
        """Get audio information"""
        try:
            y, sr = librosa.load(file_path, sr=None)
            return {
                "duration": len(y) / sr,
                "sample_rate": sr,
                "channels": 1 if len(y.shape) == 1 else y.shape[0],
                "samples": len(y)
            }
        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def extract_frames_from_video(
        video_base64: str, 
        max_frames: int = 100,
        interval: int = 5
    ) -> List[np.ndarray]:
        """
        Extract frames from video
        
        Args:
            video_base64: Base64 encoded video
            max_frames: Maximum number of frames to extract
            interval: Extract every Nth frame
            
        Returns:
            List of frame arrays
        """
        try:
            video_data = MediaProcessor.base64_to_bytes(video_base64)
            
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_file.write(video_data)
                temp_path = temp_file.name
            
            try:
                frames = []
                cap = cv2.VideoCapture(temp_path)
                
                frame_count = 0
                extracted_count = 0
                
                while cap.isOpened() and extracted_count < max_frames:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    if frame_count % interval == 0:
                        frames.append(frame)
                        extracted_count += 1
                    
                    frame_count += 1
                
                cap.release()
                return frames
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Error extracting frames: {e}")
            return []
    
    @staticmethod
    def extract_audio_segments(
        audio_base64: str,
        segment_duration: float = 3.0,
        overlap: float = 0.5
    ) -> List[np.ndarray]:
        """
        Extract audio segments with overlap
        
        Args:
            audio_base64: Base64 encoded audio
            segment_duration: Duration of each segment in seconds
            overlap: Overlap between segments (0-1)
            
        Returns:
            List of audio segment arrays
        """
        try:
            audio_data = MediaProcessor.base64_to_bytes(audio_base64)
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            try:
                y, sr = librosa.load(temp_path, sr=16000)
                
                segment_samples = int(segment_duration * sr)
                step_samples = int(segment_samples * (1 - overlap))
                
                segments = []
                start = 0
                
                while start + segment_samples <= len(y):
                    segment = y[start:start + segment_samples]
                    segments.append(segment)
                    start += step_samples
                
                # Add the last segment if there's remaining audio
                if start < len(y):
                    last_segment = y[start:]
                    if len(last_segment) > segment_samples // 2:  # Only if significant duration
                        # Pad to standard length
                        padded = np.pad(last_segment, (0, max(0, segment_samples - len(last_segment))))
                        segments.append(padded)
                
                return segments
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Error extracting audio segments: {e}")
            return []
    
    @staticmethod
    def resize_image(image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """Resize image while maintaining aspect ratio"""
        height, width = image.shape[:2]
        target_width, target_height = target_size
        
        # Calculate scaling factor
        scale = min(target_width / width, target_height / height)
        
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Resize image
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # Pad to target size
        delta_w = target_width - new_width
        delta_h = target_height - new_height
        top, bottom = delta_h // 2, delta_h - (delta_h // 2)
        left, right = delta_w // 2, delta_w - (delta_w // 2)
        
        padded = cv2.copyMakeBorder(
            resized, top, bottom, left, right, 
            cv2.BORDER_CONSTANT, value=[0, 0, 0]
        )
        
        return padded
    
    @staticmethod
    def normalize_image(image: np.ndarray) -> np.ndarray:
        """Normalize image for model input"""
        # Convert to float32 and normalize to [0, 1]
        normalized = image.astype(np.float32) / 255.0
        
        # Apply standard normalization (ImageNet stats)
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        
        normalized = (normalized - mean) / std
        
        return normalized
    
    @staticmethod
    def preprocess_audio(audio: np.ndarray, sr: int = 16000) -> np.ndarray:
        """Preprocess audio for model input"""
        # Normalize amplitude
        audio = audio / (np.max(np.abs(audio)) + 1e-8)
        
        # Apply pre-emphasis filter
        pre_emphasis = 0.97
        audio = np.append(audio[0], audio[1:] - pre_emphasis * audio[:-1])
        
        return audio
    
    @staticmethod
    def calculate_content_hash(media_data: bytes) -> str:
        """Calculate hash of media content for integrity verification"""
        return hashlib.sha256(media_data).hexdigest()
    
    @staticmethod
    def extract_metadata(file_path: str) -> Dict[str, Any]:
        """Extract metadata from media file"""
        try:
            metadata = {}
            
            # Get file stats
            stat = os.stat(file_path)
            metadata.update({
                "file_size": stat.st_size,
                "created_time": stat.st_ctime,
                "modified_time": stat.st_mtime
            })
            
            # Try to extract EXIF data for images
            try:
                from PIL import Image
                from PIL.ExifTags import TAGS
                
                with Image.open(file_path) as image:
                    exif_data = image._getexif()
                    if exif_data:
                        exif = {
                            TAGS[key]: value
                            for key, value in exif_data.items()
                            if key in TAGS
                        }
                        metadata["exif"] = exif
            except:
                pass
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {}
    
    @staticmethod
    def compress_for_storage(image: np.ndarray, quality: int = 80) -> bytes:
        """Compress image for storage"""
        try:
            # Convert to PIL Image
            if len(image.shape) == 3:
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            else:
                pil_image = Image.fromarray(image)
            
            # Compress
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG', quality=quality, optimize=True)
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error compressing image: {e}")
            raise 