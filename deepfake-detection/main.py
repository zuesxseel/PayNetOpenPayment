"""
Main Deepfake Detection Service
"""
import asyncio
import time
import uuid
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from loguru import logger

from .models.schemas import (
    DeepfakeDetectionRequest, DeepfakeAnalysis, MediaInfo, MediaType,
    DetectionMethod, AuthenticityLevel, DeepfakeType, FrameAnalysis,
    AudioSegmentAnalysis, DetectionProgress, ProcessingStatus
)
from .detection.visual_detector import VisualDeepfakeDetector
from .detection.audio_detector import AudioDeepfakeDetector
from .utils.media_utils import MediaProcessor
from .config.settings import settings


class ComprehensiveDeepfakeDetector:
    """Main deepfake detection service that orchestrates all detection methods"""
    
    def __init__(self):
        # Initialize individual detectors
        self.visual_detector = VisualDeepfakeDetector()
        self.audio_detector = AudioDeepfakeDetector()
        
        logger.info("Comprehensive deepfake detector initialized")
    
    async def detect_deepfake(
        self,
        request: DeepfakeDetectionRequest,
        progress_callback: Optional[Callable[[DetectionProgress], None]] = None
    ) -> DeepfakeAnalysis:
        """
        Perform comprehensive deepfake detection
        
        Args:
            request: Detection request with media data
            progress_callback: Optional callback for progress updates
            
        Returns:
            Comprehensive deepfake analysis result
        """
        detection_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            await self._emit_progress(
                detection_id, "Starting analysis", ProcessingStatus.PROCESSING, 0, progress_callback
            )
            
            # Validate and extract media information
            media_info = self._extract_media_info(request.media_data)
            if not media_info["valid"]:
                raise ValueError(f"Invalid media: {media_info.get('error', 'Unknown error')}")
            
            await self._emit_progress(
                detection_id, "Media validation complete", ProcessingStatus.PROCESSING, 10, progress_callback
            )
            
            # Create media info object
            media_info_obj = MediaInfo(
                file_type=MediaType(media_info["media_type"]),
                file_size=media_info["file_size"],
                duration=media_info.get("duration"),
                resolution=media_info.get("resolution"),
                fps=media_info.get("fps"),
                sample_rate=media_info.get("sample_rate"),
                channels=media_info.get("channels")
            )
            
            # Initialize result
            result = DeepfakeAnalysis(
                detection_id=detection_id,
                timestamp=datetime.utcnow(),
                media_info=media_info_obj,
                is_deepfake=False,
                overall_probability=0.0,
                confidence_score=0.0,
                authenticity_level=AuthenticityLevel.AUTHENTIC,
                detected_techniques=[],
                frame_analysis=[],
                audio_segments=[],
                media_quality={},
                processing_quality={},
                anomalies=[],
                evidence=[],
                artifacts=[],
                total_processing_time=0.0,
                model_versions=self._get_model_versions(),
                metadata=request.options
            )
            
            # Perform detection based on media type and requested methods
            if media_info_obj.file_type == MediaType.IMAGE:
                await self._process_image(request, result, progress_callback)
            elif media_info_obj.file_type == MediaType.VIDEO:
                await self._process_video(request, result, progress_callback)
            elif media_info_obj.file_type == MediaType.AUDIO:
                await self._process_audio(request, result, progress_callback)
            
            # Calculate overall results
            self._calculate_overall_result(result)
            
            # Generate evidence and recommendations
            self._generate_evidence_and_artifacts(result)
            
            result.total_processing_time = time.time() - start_time
            
            await self._emit_progress(
                detection_id, "Analysis complete", ProcessingStatus.COMPLETED, 100, progress_callback
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in deepfake detection: {e}")
            
            # Create error result
            error_result = DeepfakeAnalysis(
                detection_id=detection_id,
                timestamp=datetime.utcnow(),
                media_info=MediaInfo(
                    file_type=MediaType.IMAGE,
                    file_size=0
                ),
                is_deepfake=False,
                overall_probability=0.5,
                confidence_score=0.0,
                authenticity_level=AuthenticityLevel.SUSPICIOUS,
                detected_techniques=[],
                frame_analysis=[],
                audio_segments=[],
                media_quality={},
                processing_quality={},
                anomalies=[f"Processing error: {str(e)}"],
                evidence=[],
                artifacts=[],
                total_processing_time=time.time() - start_time,
                model_versions=self._get_model_versions(),
                metadata=request.options
            )
            
            await self._emit_progress(
                detection_id, "Analysis failed", ProcessingStatus.FAILED, 0, progress_callback
            )
            
            return error_result
    
    async def _process_image(
        self,
        request: DeepfakeDetectionRequest,
        result: DeepfakeAnalysis,
        progress_callback: Optional[Callable[[DetectionProgress], None]]
    ):
        """Process image for deepfake detection"""
        try:
            await self._emit_progress(
                result.detection_id, "Analyzing image", ProcessingStatus.PROCESSING, 20, progress_callback
            )
            
            # Convert base64 to image
            image = MediaProcessor.base64_to_opencv(request.media_data)
            
            # Visual analysis
            if DetectionMethod.VISUAL_ANALYSIS in request.detection_methods or DetectionMethod.ENSEMBLE in request.detection_methods:
                visual_result = self.visual_detector.detect_deepfake_in_image(image)
                result.visual_analysis = visual_result
                
                await self._emit_progress(
                    result.detection_id, "Visual analysis complete", ProcessingStatus.PROCESSING, 80, progress_callback
                )
            
            # Calculate media quality
            result.media_quality = MediaProcessor.calculate_image_quality(image)
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            result.anomalies.append(f"Image processing error: {str(e)}")
    
    async def _process_video(
        self,
        request: DeepfakeDetectionRequest,
        result: DeepfakeAnalysis,
        progress_callback: Optional[Callable[[DetectionProgress], None]]
    ):
        """Process video for deepfake detection"""
        try:
            await self._emit_progress(
                result.detection_id, "Extracting video frames", ProcessingStatus.PROCESSING, 20, progress_callback
            )
            
            # Extract frames
            frames = MediaProcessor.extract_frames_from_video(
                request.media_data,
                max_frames=settings.max_frames_per_video,
                interval=settings.frame_extraction_interval
            )
            
            if not frames:
                result.anomalies.append("No frames could be extracted from video")
                return
            
            await self._emit_progress(
                result.detection_id, f"Analyzing {len(frames)} frames", ProcessingStatus.PROCESSING, 40, progress_callback
            )
            
            # Visual analysis on frames
            if DetectionMethod.VISUAL_ANALYSIS in request.detection_methods or DetectionMethod.ENSEMBLE in request.detection_methods:
                frame_analyses = self.visual_detector.detect_deepfake_in_frames(frames)
                result.frame_analysis = frame_analyses
                
                # Create overall visual result from frame analyses
                if frame_analyses:
                    max_prob = max(frame.deepfake_probability for frame in frame_analyses)
                    avg_prob = sum(frame.deepfake_probability for frame in frame_analyses) / len(frame_analyses)
                    
                    # Use temporal analysis for video
                    temporal_features = self._analyze_temporal_consistency(frame_analyses)
                    
                    from .models.schemas import DetectionResult, TemporalFeatures
                    result.visual_analysis = DetectionResult(
                        method=DetectionMethod.VISUAL_ANALYSIS,
                        probability=max_prob,
                        confidence=self._calculate_temporal_confidence(frame_analyses),
                        authenticity_level=self._determine_authenticity_level(max_prob),
                        processing_time=sum(f.deepfake_probability for f in frame_analyses),  # Placeholder
                        features=temporal_features
                    )
                
                await self._emit_progress(
                    result.detection_id, "Frame analysis complete", ProcessingStatus.PROCESSING, 70, progress_callback
                )
            
            # Audio analysis if video has audio
            if result.media_info.has_audio and (DetectionMethod.AUDIO_ANALYSIS in request.detection_methods or DetectionMethod.ENSEMBLE in request.detection_methods):
                # Extract audio from video (simplified - would need actual audio extraction)
                # For now, skip audio analysis for video
                pass
            
            # Temporal consistency analysis
            if DetectionMethod.TEMPORAL_ANALYSIS in request.detection_methods or DetectionMethod.ENSEMBLE in request.detection_methods:
                temporal_result = self._perform_temporal_analysis(frames, result.frame_analysis)
                result.temporal_analysis = temporal_result
                
                await self._emit_progress(
                    result.detection_id, "Temporal analysis complete", ProcessingStatus.PROCESSING, 90, progress_callback
                )
            
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            result.anomalies.append(f"Video processing error: {str(e)}")
    
    async def _process_audio(
        self,
        request: DeepfakeDetectionRequest,
        result: DeepfakeAnalysis,
        progress_callback: Optional[Callable[[DetectionProgress], None]]
    ):
        """Process audio for deepfake detection"""
        try:
            await self._emit_progress(
                result.detection_id, "Analyzing audio", ProcessingStatus.PROCESSING, 30, progress_callback
            )
            
            # Audio analysis
            if DetectionMethod.AUDIO_ANALYSIS in request.detection_methods or DetectionMethod.ENSEMBLE in request.detection_methods:
                audio_result = self.audio_detector.detect_deepfake_in_audio(request.media_data)
                result.audio_analysis = audio_result
                
                await self._emit_progress(
                    result.detection_id, "Audio analysis complete", ProcessingStatus.PROCESSING, 80, progress_callback
                )
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            result.anomalies.append(f"Audio processing error: {str(e)}")
    
    def _analyze_temporal_consistency(self, frame_analyses: List[FrameAnalysis]) -> Any:
        """Analyze temporal consistency across frames"""
        try:
            if len(frame_analyses) < 2:
                return None
            
            # Calculate frame-to-frame consistency
            consistency_scores = []
            for i in range(1, len(frame_analyses)):
                prev_prob = frame_analyses[i-1].deepfake_probability
                curr_prob = frame_analyses[i].deepfake_probability
                consistency = 1.0 - abs(prev_prob - curr_prob)
                consistency_scores.append(consistency)
            
            frame_consistency = sum(consistency_scores) / len(consistency_scores)
            
            # Analyze motion patterns (simplified)
            motion_patterns = 0.5  # Placeholder
            
            # Expression continuity
            expression_continuity = 0.5  # Placeholder
            
            # Blink patterns
            blink_patterns = 0.5  # Placeholder
            
            # Identity consistency
            identity_consistency = frame_consistency
            
            # Temporal artifacts
            temporal_artifacts = 1.0 - frame_consistency
            
            from .models.schemas import TemporalFeatures
            return TemporalFeatures(
                frame_consistency=frame_consistency,
                motion_patterns=motion_patterns,
                expression_continuity=expression_continuity,
                blink_patterns=blink_patterns,
                identity_consistency=identity_consistency,
                temporal_artifacts=temporal_artifacts
            )
            
        except Exception as e:
            logger.error(f"Error analyzing temporal consistency: {e}")
            return None
    
    def _perform_temporal_analysis(self, frames: List, frame_analyses: List[FrameAnalysis]) -> Any:
        """Perform temporal analysis on video frames"""
        try:
            temporal_features = self._analyze_temporal_consistency(frame_analyses)
            
            if temporal_features:
                # Calculate temporal probability
                temporal_prob = temporal_features.temporal_artifacts
                
                # Calculate confidence
                confidence = temporal_features.frame_consistency
                
                # Determine authenticity
                authenticity = self._determine_authenticity_level(temporal_prob)
                
                from .models.schemas import DetectionResult
                return DetectionResult(
                    method=DetectionMethod.TEMPORAL_ANALYSIS,
                    probability=temporal_prob,
                    confidence=confidence,
                    authenticity_level=authenticity,
                    processing_time=0.0,  # Placeholder
                    features=temporal_features
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error in temporal analysis: {e}")
            return None
    
    def _calculate_temporal_confidence(self, frame_analyses: List[FrameAnalysis]) -> float:
        """Calculate confidence from temporal analysis"""
        if not frame_analyses:
            return 0.0
        
        # Calculate variance in probabilities (lower variance = higher confidence)
        probabilities = [frame.deepfake_probability for frame in frame_analyses]
        variance = sum((p - sum(probabilities) / len(probabilities)) ** 2 for p in probabilities) / len(probabilities)
        
        # Convert variance to confidence (inverse relationship)
        confidence = max(0.0, 1.0 - variance * 4)  # Scale appropriately
        
        return confidence
    
    def _calculate_overall_result(self, result: DeepfakeAnalysis):
        """Calculate overall deepfake detection result"""
        try:
            probabilities = []
            confidences = []
            
            # Collect probabilities from individual analyses
            if result.visual_analysis:
                probabilities.append(result.visual_analysis.probability)
                confidences.append(result.visual_analysis.confidence)
            
            if result.audio_analysis:
                probabilities.append(result.audio_analysis.probability)
                confidences.append(result.audio_analysis.confidence)
            
            if result.temporal_analysis:
                probabilities.append(result.temporal_analysis.probability)
                confidences.append(result.temporal_analysis.confidence)
            
            if probabilities:
                # Use weighted average based on confidence
                if confidences and sum(confidences) > 0:
                    weights = [c / sum(confidences) for c in confidences]
                    overall_probability = sum(p * w for p, w in zip(probabilities, weights))
                else:
                    overall_probability = sum(probabilities) / len(probabilities)
                
                # Overall confidence is the average of individual confidences
                overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            else:
                overall_probability = 0.0
                overall_confidence = 0.0
            
            # Determine if deepfake
            is_deepfake = overall_probability >= settings.deepfake_threshold
            
            # Determine authenticity level
            authenticity_level = self._determine_authenticity_level(overall_probability)
            
            # Detect techniques (simplified)
            detected_techniques = self._detect_deepfake_techniques(result)
            
            # Update result
            result.overall_probability = overall_probability
            result.confidence_score = overall_confidence
            result.is_deepfake = is_deepfake
            result.authenticity_level = authenticity_level
            result.detected_techniques = detected_techniques
            
        except Exception as e:
            logger.error(f"Error calculating overall result: {e}")
    
    def _detect_deepfake_techniques(self, result: DeepfakeAnalysis) -> List[DeepfakeType]:
        """Detect specific deepfake techniques used"""
        techniques = []
        
        try:
            # Analyze visual features for technique detection
            if result.visual_analysis and result.visual_analysis.features:
                features = result.visual_analysis.features
                
                # Face swap detection (high texture inconsistency + lighting issues)
                if hasattr(features, 'texture_inconsistency') and hasattr(features, 'lighting_consistency'):
                    if features.texture_inconsistency > 0.6 and features.lighting_consistency > 0.6:
                        techniques.append(DeepfakeType.FACE_SWAP)
                
                # Face reenactment detection (high compression artifacts + landmark instability)
                if hasattr(features, 'compression_artifacts') and hasattr(features, 'facial_landmark_stability'):
                    if features.compression_artifacts > 0.7 and features.facial_landmark_stability < 0.4:
                        techniques.append(DeepfakeType.FACE_REENACTMENT)
            
            # Audio-based technique detection
            if result.audio_analysis and result.audio_analysis.features:
                if result.overall_probability > 0.6:
                    techniques.append(DeepfakeType.SPEECH_SYNTHESIS)
            
            # If no specific technique detected but probability is high
            if not techniques and result.overall_probability > settings.deepfake_threshold:
                techniques.append(DeepfakeType.UNKNOWN)
                
        except Exception as e:
            logger.error(f"Error detecting deepfake techniques: {e}")
        
        return techniques
    
    def _generate_evidence_and_artifacts(self, result: DeepfakeAnalysis):
        """Generate evidence and artifacts for the detection"""
        try:
            evidence = []
            artifacts = []
            
            # Visual evidence
            if result.visual_analysis and result.visual_analysis.features:
                features = result.visual_analysis.features
                
                if hasattr(features, 'texture_inconsistency') and features.texture_inconsistency > 0.5:
                    evidence.append("Inconsistent facial texture patterns detected")
                    artifacts.append("texture_inconsistency")
                
                if hasattr(features, 'lighting_consistency') and features.lighting_consistency > 0.5:
                    evidence.append("Lighting inconsistencies between face and background")
                    artifacts.append("lighting_inconsistency")
                
                if hasattr(features, 'compression_artifacts') and features.compression_artifacts > 0.6:
                    evidence.append("Unusual compression artifacts around face region")
                    artifacts.append("compression_artifacts")
            
            # Audio evidence
            if result.audio_analysis:
                if result.audio_analysis.probability > 0.6:
                    evidence.append("Synthetic speech patterns detected")
                    artifacts.append("synthetic_speech")
            
            # Temporal evidence
            if result.temporal_analysis and result.temporal_analysis.features:
                features = result.temporal_analysis.features
                
                if hasattr(features, 'frame_consistency') and features.frame_consistency < 0.4:
                    evidence.append("Inconsistent identity across video frames")
                    artifacts.append("identity_inconsistency")
                
                if hasattr(features, 'temporal_artifacts') and features.temporal_artifacts > 0.6:
                    evidence.append("Temporal artifacts indicating frame manipulation")
                    artifacts.append("temporal_manipulation")
            
            result.evidence = evidence
            result.artifacts = artifacts
            
        except Exception as e:
            logger.error(f"Error generating evidence: {e}")
    
    def _determine_authenticity_level(self, probability: float) -> AuthenticityLevel:
        """Determine authenticity level from probability"""
        if probability >= 0.8:
            return AuthenticityLevel.DEEPFAKE
        elif probability >= settings.deepfake_threshold:
            return AuthenticityLevel.LIKELY_FAKE
        elif probability >= 0.3:
            return AuthenticityLevel.SUSPICIOUS
        elif probability >= 0.1:
            return AuthenticityLevel.LIKELY_AUTHENTIC
        else:
            return AuthenticityLevel.AUTHENTIC
    
    def _extract_media_info(self, media_base64: str) -> Dict[str, Any]:
        """Extract media information from base64 data"""
        return MediaProcessor.validate_media(media_base64)
    
    def _get_model_versions(self) -> Dict[str, str]:
        """Get versions of all models"""
        return {
            "visual_detector": "v1.0.0",
            "audio_detector": "v1.0.0",
            "ensemble": "v1.0.0"
        }
    
    async def _emit_progress(
        self,
        detection_id: str,
        message: str,
        status: ProcessingStatus,
        progress: int,
        callback: Optional[Callable[[DetectionProgress], None]]
    ):
        """Emit progress update"""
        if callback:
            try:
                progress_update = DetectionProgress(
                    detection_id=detection_id,
                    status=status,
                    progress=float(progress),
                    current_step=message,
                    estimated_time_remaining=None
                )
                callback(progress_update)
            except Exception as e:
                logger.error(f"Error emitting progress: {e}")
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        try:
            return {
                "visual_detector": True,
                "audio_detector": True,
                "gpu_available": torch.cuda.is_available() if 'torch' in globals() else False,
                "models_loaded": ["visual", "audio"],
                "memory_usage": "N/A",
                "active_sessions": 0
            }
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {"error": str(e)}


# Global instance
deepfake_detector = ComprehensiveDeepfakeDetector()


# Example usage
async def main():
    """Example usage of deepfake detection"""
    
    # Example image detection
    print("=== Deepfake Detection Example ===")
    
    # Placeholder base64 image data (you would provide real image data)
    sample_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    def progress_callback(progress: DetectionProgress):
        print(f"Progress: {progress.progress}% - {progress.current_step}")
    
    try:
        # Create detection request
        request = DeepfakeDetectionRequest(
            media_data=sample_image_base64,
            media_type=MediaType.IMAGE,
            detection_methods=[DetectionMethod.VISUAL_ANALYSIS],
            options={"high_accuracy": True}
        )
        
        # Perform detection
        result = await deepfake_detector.detect_deepfake(request, progress_callback)
        
        # Display results
        print(f"\nDetection Results:")
        print(f"Detection ID: {result.detection_id}")
        print(f"Is Deepfake: {result.is_deepfake}")
        print(f"Probability: {result.overall_probability:.3f}")
        print(f"Confidence: {result.confidence_score:.3f}")
        print(f"Authenticity Level: {result.authenticity_level}")
        print(f"Processing Time: {result.total_processing_time:.3f}s")
        
        if result.detected_techniques:
            print(f"Detected Techniques: {', '.join(result.detected_techniques)}")
        
        if result.evidence:
            print(f"Evidence: {', '.join(result.evidence)}")
        
        if result.anomalies:
            print(f"Anomalies: {', '.join(result.anomalies)}")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import torch
    asyncio.run(main()) 