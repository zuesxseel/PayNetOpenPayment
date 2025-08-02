"""
Main AI Verification Service
Comprehensive identity verification system that integrates all AI components
"""
import asyncio
import time
import uuid
from typing import Dict, List, Optional, Callable
from datetime import datetime
from loguru import logger

from .models.schemas import (
    VerificationInput, ComprehensiveVerificationResult, VerificationProgress,
    DocumentType, VerificationStatus, OCRResult, FaceRecognitionResult,
    LivenessResult, DocumentVerificationResult, DatabaseVerificationResult
)
from .ocr.ocr_service import OCRService
from .face_recognition.face_service import FaceRecognitionService
from .liveness_detection.liveness_service import LivenessDetectionService
from .document_verification.document_service import DocumentVerificationService
from .database_verification.database_service import DatabaseVerificationService
from .config.settings import settings


class ComprehensiveAIVerificationService:
    """
    Main service that orchestrates all AI verification components
    This matches the verification process shown in the React Native screen
    """
    
    def __init__(self):
        # Initialize all services
        self.ocr_service = OCRService()
        self.face_service = FaceRecognitionService()
        self.liveness_service = LivenessDetectionService()
        self.document_service = DocumentVerificationService()
        self.database_service = DatabaseVerificationService()
        
        logger.info("AI Verification Service initialized successfully")
    
    async def perform_comprehensive_verification(
        self,
        verification_input: VerificationInput,
        progress_callback: Optional[Callable[[VerificationProgress], None]] = None
    ) -> ComprehensiveVerificationResult:
        """
        Perform comprehensive identity verification
        This follows the exact steps shown in the React Native verification screen
        
        Args:
            verification_input: Input data (document image, selfie, document type)
            progress_callback: Optional callback for progress updates
            
        Returns:
            Comprehensive verification result
        """
        verification_id = str(uuid.uuid4())
        start_time = time.time()
        
        logger.info(f"Starting comprehensive verification {verification_id}")
        
        # Initialize result
        result = ComprehensiveVerificationResult(
            verification_id=verification_id,
            timestamp=datetime.utcnow(),
            success=False,
            overall_score=0.0,
            status=VerificationStatus.PROCESSING,
            errors=[],
            warnings=[],
            recommendations=[],
            total_processing_time=0.0,
            input_metadata=verification_input.metadata,
            model_versions=self._get_model_versions()
        )
        
        try:
            # Step 1: Initialize verification engine
            await self._emit_progress(
                "Initializing verification engine...",
                VerificationStatus.PROCESSING,
                5,
                progress_callback
            )
            await asyncio.sleep(0.5)  # Simulate processing time
            
            # Step 2: OCR - Extract text from ID
            await self._emit_progress(
                "ID image received. Extracting text from ID...",
                VerificationStatus.PROCESSING,
                15,
                progress_callback
            )
            
            ocr_result = await self._perform_ocr_extraction(verification_input)
            result.ocr_result = ocr_result
            
            if ocr_result.success:
                extracted_name = ocr_result.extracted_data.name or "Unknown"
                extracted_nric = ocr_result.extracted_data.nric or "Unknown"
                await self._emit_progress(
                    f"Extracted Name: {extracted_name}, NRIC: {extracted_nric}",
                    VerificationStatus.PROCESSING,
                    25,
                    progress_callback
                )
            else:
                result.errors.append("Failed to extract text from document")
                await self._emit_progress(
                    "Text extraction failed",
                    VerificationStatus.ERROR,
                    25,
                    progress_callback
                )
            
            # Step 3: Document Authenticity Verification
            await self._emit_progress(
                "Verifying ID card authenticity (hologram, layout, etc.)...",
                VerificationStatus.PROCESSING,
                35,
                progress_callback
            )
            
            doc_verification_result = await self._perform_document_verification(verification_input)
            result.document_verification_result = doc_verification_result
            
            if doc_verification_result.success and doc_verification_result.is_authentic:
                await self._emit_progress(
                    "ID document validity check passed.",
                    VerificationStatus.PROCESSING,
                    45,
                    progress_callback
                )
            else:
                result.errors.append("Document authenticity check failed")
                await self._emit_progress(
                    "ID document validity check failed - suspicious patterns detected.",
                    VerificationStatus.ERROR,
                    45,
                    progress_callback
                )
            
            # Step 4: Face Recognition
            await self._emit_progress(
                "Performing facial recognition match...",
                VerificationStatus.PROCESSING,
                55,
                progress_callback
            )
            
            face_result = await self._perform_face_recognition(verification_input)
            result.face_recognition_result = face_result
            
            await self._emit_progress(
                "Comparing live selfie to ID photo...",
                VerificationStatus.PROCESSING,
                60,
                progress_callback
            )
            
            if face_result.success and face_result.is_match:
                confidence_pct = int(face_result.match_score * 100)
                await self._emit_progress(
                    f"Face match successful ({confidence_pct}% confidence).",
                    VerificationStatus.PROCESSING,
                    65,
                    progress_callback
                )
            else:
                confidence_pct = int(face_result.match_score * 100) if face_result.success else 0
                result.errors.append("Face recognition match failed")
                await self._emit_progress(
                    f"Face match failed ({confidence_pct}% confidence) - insufficient similarity.",
                    VerificationStatus.ERROR,
                    65,
                    progress_callback
                )
            
            # Step 5: Liveness Detection
            await self._emit_progress(
                "Conducting liveness check on selfie...",
                VerificationStatus.PROCESSING,
                70,
                progress_callback
            )
            
            liveness_result = await self._perform_liveness_detection(verification_input)
            result.liveness_result = liveness_result
            
            if liveness_result.success and liveness_result.is_live:
                await self._emit_progress(
                    "Liveness check passed – user is physically present.",
                    VerificationStatus.PROCESSING,
                    80,
                    progress_callback
                )
            else:
                result.errors.append("Liveness detection failed")
                await self._emit_progress(
                    "Liveness check failed - potential spoofing detected.",
                    VerificationStatus.ERROR,
                    80,
                    progress_callback
                )
            
            # Step 6: Database Verification
            await self._emit_progress(
                "Connecting to national identity database...",
                VerificationStatus.PROCESSING,
                85,
                progress_callback
            )
            
            if ocr_result.success and ocr_result.extracted_data.nric:
                await self._emit_progress(
                    "Cross-checking NRIC and personal details with government records...",
                    VerificationStatus.PROCESSING,
                    90,
                    progress_callback
                )
                
                db_result = await self._perform_database_verification(ocr_result.extracted_data)
                result.database_verification_result = db_result
                
                if db_result.success and db_result.is_valid:
                    await self._emit_progress(
                        "Personal details verified with official records.",
                        VerificationStatus.PROCESSING,
                        95,
                        progress_callback
                    )
                else:
                    result.errors.append("Database verification failed")
                    await self._emit_progress(
                        "Personal details mismatch with official records.",
                        VerificationStatus.ERROR,
                        95,
                        progress_callback
                    )
            else:
                result.warnings.append("Skipped database verification due to missing NRIC")
                await self._emit_progress(
                    "Database verification skipped - no NRIC extracted",
                    VerificationStatus.PROCESSING,
                    95,
                    progress_callback
                )
            
            # Calculate overall results
            overall_score, status = self._calculate_overall_result(result)
            result.overall_score = overall_score
            result.status = status
            result.success = status == VerificationStatus.PASSED
            
            # Generate recommendations
            result.recommendations = self._generate_recommendations(result)
            
            # Final step
            if result.success:
                await self._emit_progress(
                    "All verification checks passed!",
                    VerificationStatus.PROCESSING,
                    98,
                    progress_callback
                )
                await self._emit_progress(
                    "Account creation in progress...",
                    VerificationStatus.PASSED,
                    100,
                    progress_callback
                )
            else:
                await self._emit_progress(
                    "Verification failed - multiple checks did not pass.",
                    VerificationStatus.FAILED,
                    100,
                    progress_callback
                )
            
            result.total_processing_time = time.time() - start_time
            
            logger.info(f"Verification {verification_id} completed with status: {status}")
            return result
            
        except Exception as e:
            result.total_processing_time = time.time() - start_time
            result.success = False
            result.status = VerificationStatus.ERROR
            result.errors.append(f"System error: {str(e)}")
            
            logger.error(f"Verification {verification_id} failed with error: {e}")
            
            if progress_callback:
                await self._emit_progress(
                    "Verification failed due to system error",
                    VerificationStatus.ERROR,
                    100,
                    progress_callback
                )
            
            return result
    
    async def _perform_ocr_extraction(self, verification_input: VerificationInput) -> OCRResult:
        """Perform OCR text extraction"""
        try:
            # Run OCR in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.ocr_service.extract_text_from_document,
                verification_input.document_image,
                verification_input.document_type
            )
            return result
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return OCRResult(
                success=False,
                confidence=0.0,
                extracted_data={},
                raw_text="",
                bounding_boxes=[],
                processing_time=0.0,
                engine_used="unknown"
            )
    
    async def _perform_face_recognition(self, verification_input: VerificationInput) -> FaceRecognitionResult:
        """Perform face recognition comparison"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.face_service.compare_faces,
                verification_input.document_image,
                verification_input.selfie_image
            )
            return result
        except Exception as e:
            logger.error(f"Face recognition error: {e}")
            return FaceRecognitionResult(
                success=False,
                is_match=False,
                match_score=0.0,
                confidence=0.0,
                threshold_used=0.85,
                faces_detected=[],
                processing_time=0.0
            )
    
    async def _perform_liveness_detection(self, verification_input: VerificationInput) -> LivenessResult:
        """Perform liveness detection"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.liveness_service.detect_liveness,
                verification_input.selfie_image
            )
            return result
        except Exception as e:
            logger.error(f"Liveness detection error: {e}")
            return LivenessResult(
                success=False,
                is_live=False,
                liveness_score=0.0,
                confidence=0.0,
                spoofing_attempts=[],
                blink_detected=False,
                motion_detected=False,
                processing_time=0.0
            )
    
    async def _perform_document_verification(self, verification_input: VerificationInput) -> DocumentVerificationResult:
        """Perform document authenticity verification"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.document_service.verify_document_authenticity,
                verification_input.document_image,
                verification_input.document_type
            )
            return result
        except Exception as e:
            logger.error(f"Document verification error: {e}")
            return DocumentVerificationResult(
                success=False,
                is_authentic=False,
                confidence=0.0,
                document_type=verification_input.document_type,
                issuer="Unknown",
                security_features=[],
                template_match_score=0.0,
                tampering_detected=True,
                processing_time=0.0
            )
    
    async def _perform_database_verification(self, extracted_data) -> DatabaseVerificationResult:
        """Perform database verification"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.database_service.verify_identity,
                extracted_data.nric,
                extracted_data.name,
                extracted_data.date_of_birth
            )
            return result
        except Exception as e:
            logger.error(f"Database verification error: {e}")
            return DatabaseVerificationResult(
                success=False,
                is_valid=False,
                verification_status="error",
                matched_records=[],
                blacklist_check=False,
                sanctions_check=False,
                processing_time=0.0
            )
    
    def _calculate_overall_result(self, result: ComprehensiveVerificationResult) -> tuple[float, VerificationStatus]:
        """Calculate overall verification score and status"""
        try:
            # Define weights for each component
            weights = {
                'ocr': 0.20,
                'document': 0.25,
                'face': 0.25,
                'liveness': 0.20,
                'database': 0.10
            }
            
            total_score = 0.0
            total_weight = 0.0
            
            # OCR score
            if result.ocr_result and result.ocr_result.success:
                total_score += result.ocr_result.confidence * weights['ocr']
                total_weight += weights['ocr']
            
            # Document verification score
            if result.document_verification_result and result.document_verification_result.success:
                doc_score = 1.0 if result.document_verification_result.is_authentic else 0.0
                total_score += doc_score * weights['document']
                total_weight += weights['document']
            
            # Face recognition score
            if result.face_recognition_result and result.face_recognition_result.success:
                face_score = result.face_recognition_result.match_score if result.face_recognition_result.is_match else 0.0
                total_score += face_score * weights['face']
                total_weight += weights['face']
            
            # Liveness detection score
            if result.liveness_result and result.liveness_result.success:
                liveness_score = result.liveness_result.liveness_score if result.liveness_result.is_live else 0.0
                total_score += liveness_score * weights['liveness']
                total_weight += weights['liveness']
            
            # Database verification score
            if result.database_verification_result and result.database_verification_result.success:
                db_score = 1.0 if result.database_verification_result.is_valid else 0.0
                total_score += db_score * weights['database']
                total_weight += weights['database']
            
            # Calculate final score
            overall_score = total_score / total_weight if total_weight > 0 else 0.0
            
            # Determine status based on score and errors
            if result.errors:
                if overall_score >= 0.6:
                    status = VerificationStatus.REVIEW_REQUIRED
                else:
                    status = VerificationStatus.FAILED
            else:
                if overall_score >= 0.85:
                    status = VerificationStatus.PASSED
                elif overall_score >= 0.6:
                    status = VerificationStatus.REVIEW_REQUIRED
                else:
                    status = VerificationStatus.FAILED
            
            return overall_score, status
            
        except Exception as e:
            logger.error(f"Error calculating overall result: {e}")
            return 0.0, VerificationStatus.ERROR
    
    def _generate_recommendations(self, result: ComprehensiveVerificationResult) -> List[str]:
        """Generate user-friendly recommendations based on verification results"""
        recommendations = []
        
        # OCR recommendations
        if result.ocr_result and not result.ocr_result.success:
            recommendations.extend([
                "Ensure document image is clear and well-lit",
                "Hold camera steady when capturing document",
                "Make sure entire document is visible in frame"
            ])
        
        # Face recognition recommendations
        if result.face_recognition_result and not result.face_recognition_result.is_match:
            recommendations.extend([
                "Ensure your face is clearly visible in both images",
                "Use good lighting when taking selfie",
                "Look directly at camera"
            ])
        
        # Liveness recommendations
        if result.liveness_result and not result.liveness_result.is_live:
            recommendations.extend([
                "Take a live selfie, not a photo of a photo",
                "Ensure you are the only person in frame",
                "Avoid reflective surfaces behind you"
            ])
        
        # Document verification recommendations
        if result.document_verification_result and not result.document_verification_result.is_authentic:
            recommendations.extend([
                "Ensure document is authentic and not damaged",
                "Check that all security features are visible",
                "Use original document, not a photocopy"
            ])
        
        # Database verification recommendations
        if result.database_verification_result and not result.database_verification_result.is_valid:
            recommendations.extend([
                "Verify that all personal details are correct",
                "Contact support if you believe this is an error"
            ])
        
        # Add general recommendations if no specific issues
        if not recommendations:
            recommendations.append("Verification completed successfully!")
        
        return recommendations
    
    async def _emit_progress(
        self,
        message: str,
        status: VerificationStatus,
        progress: int,
        callback: Optional[Callable[[VerificationProgress], None]]
    ):
        """Emit progress update"""
        if callback:
            progress_update = VerificationProgress(
                step=message,
                status=status,
                progress=float(progress),
                message=message,
                timestamp=datetime.utcnow()
            )
            
            try:
                # Handle both sync and async callbacks
                if asyncio.iscoroutinefunction(callback):
                    await callback(progress_update)
                else:
                    callback(progress_update)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
    
    def _get_model_versions(self) -> Dict[str, str]:
        """Get versions of all AI models being used"""
        return {
            "ocr_engine": settings.ocr_engine,
            "face_recognition_model": settings.face_recognition_model,
            "liveness_model": "v1.0",
            "document_verification": "v1.0",
            "database_api": "v1.0"
        }
    
    async def get_system_health(self) -> Dict[str, bool]:
        """Check health status of all AI services"""
        health_status = {}
        
        try:
            # Check OCR service
            health_status["ocr_service"] = self.ocr_service is not None
            
            # Check Face Recognition service
            health_status["face_recognition_service"] = self.face_service is not None
            
            # Check Liveness Detection service
            health_status["liveness_detection_service"] = self.liveness_service is not None
            
            # Check Document Verification service
            health_status["document_verification_service"] = self.document_service is not None
            
            # Check Database Verification service
            health_status["database_verification_service"] = self.database_service is not None
            
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
            health_status["system_error"] = True
        
        return health_status


# Global instance
ai_verification_service = ComprehensiveAIVerificationService()


async def main():
    """Main function for testing the verification service"""
    # Example usage
    verification_input = VerificationInput(
        document_image="base64_encoded_document_image",
        selfie_image="base64_encoded_selfie_image",
        document_type=DocumentType.NRIC,
        metadata={"device": "mobile", "app_version": "1.0.0"}
    )
    
    # Progress callback function
    def progress_callback(progress: VerificationProgress):
        print(f"Progress: {progress.progress}% - {progress.message}")
    
    # Perform verification
    result = await ai_verification_service.perform_comprehensive_verification(
        verification_input,
        progress_callback
    )
    
    print(f"Verification completed with status: {result.status}")
    print(f"Overall score: {result.overall_score:.2f}")
    
    if result.errors:
        print("Errors:", result.errors)
    
    if result.recommendations:
        print("Recommendations:", result.recommendations)


if __name__ == "__main__":
    asyncio.run(main()) 