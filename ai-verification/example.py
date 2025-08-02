#!/usr/bin/env python3
"""
Example script demonstrating AI verification system usage

This script shows how to use the comprehensive AI verification system
to verify identity documents and selfies.
"""
import asyncio
import base64
from pathlib import Path

from main import ai_verification_service
from models.schemas import VerificationInput, DocumentType


async def example_verification():
    """
    Example of comprehensive identity verification
    """
    print("🤖 AI Verification System Example")
    print("=" * 50)
    
    # For this example, we'll use placeholder base64 strings
    # In a real application, you would load actual images
    
    # Sample base64 strings (these would be actual images in production)
    sample_document_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    sample_selfie_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    # Create verification input
    verification_input = VerificationInput(
        document_image=sample_document_image,
        selfie_image=sample_selfie_image,
        document_type=DocumentType.NRIC,
        metadata={
            "device": "mobile",
            "app_version": "1.0.0",
            "platform": "ios"
        }
    )
    
    # Progress callback to display verification progress
    def progress_callback(progress):
        status_emoji = {
            "processing": "⏳",
            "passed": "✅", 
            "failed": "❌",
            "error": "🚨"
        }.get(progress.status.value, "🔄")
        
        print(f"{status_emoji} {progress.progress:3.0f}% - {progress.message}")
    
    print("\n📋 Starting comprehensive verification...")
    print("-" * 50)
    
    # Perform verification
    result = await ai_verification_service.perform_comprehensive_verification(
        verification_input,
        progress_callback
    )
    
    print("\n" + "=" * 50)
    print("📊 VERIFICATION RESULTS")
    print("=" * 50)
    
    # Display overall results
    status_emoji = {
        "passed": "✅",
        "failed": "❌", 
        "review_required": "⚠️",
        "error": "🚨"
    }.get(result.status.value, "❓")
    
    print(f"Status: {status_emoji} {result.status.value.upper()}")
    print(f"Overall Score: {result.overall_score:.2f}")
    print(f"Processing Time: {result.total_processing_time:.2f}s")
    print()
    
    # Display individual component results
    print("🔍 Component Results:")
    print("-" * 30)
    
    if result.ocr_result:
        status = "✅" if result.ocr_result.success else "❌"
        print(f"  OCR Text Extraction: {status} ({result.ocr_result.confidence:.2f})")
        if result.ocr_result.success:
            extracted = result.ocr_result.extracted_data
            if extracted.name:
                print(f"    └─ Name: {extracted.name}")
            if extracted.nric:
                print(f"    └─ NRIC: {extracted.nric}")
    
    if result.face_recognition_result:
        status = "✅" if result.face_recognition_result.is_match else "❌"
        print(f"  Face Recognition: {status} ({result.face_recognition_result.match_score:.2f})")
    
    if result.liveness_result:
        status = "✅" if result.liveness_result.is_live else "❌"
        print(f"  Liveness Detection: {status} ({result.liveness_result.liveness_score:.2f})")
    
    if result.document_verification_result:
        status = "✅" if result.document_verification_result.is_authentic else "❌"
        print(f"  Document Authenticity: {status} ({result.document_verification_result.confidence:.2f})")
    
    if result.database_verification_result:
        status = "✅" if result.database_verification_result.is_valid else "❌"
        print(f"  Database Verification: {status} ({result.database_verification_result.verification_status})")
    
    # Display errors if any
    if result.errors:
        print("\n❌ Errors:")
        for error in result.errors:
            print(f"  • {error}")
    
    # Display warnings if any
    if result.warnings:
        print("\n⚠️  Warnings:")
        for warning in result.warnings:
            print(f"  • {warning}")
    
    # Display recommendations
    if result.recommendations:
        print("\n💡 Recommendations:")
        for recommendation in result.recommendations:
            print(f"  • {recommendation}")
    
    print("\n" + "=" * 50)
    return result


async def example_individual_services():
    """
    Example of using individual verification services
    """
    print("\n🔧 Individual Service Examples")
    print("=" * 50)
    
    # Sample image data
    sample_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    # Example 1: OCR Service
    print("\n1️⃣  OCR Text Extraction")
    print("-" * 30)
    try:
        from ocr.ocr_service import OCRService
        
        ocr_service = OCRService()
        ocr_result = ocr_service.extract_text_from_document(
            sample_image, 
            DocumentType.NRIC
        )
        
        if ocr_result.success:
            print(f"✅ OCR Success - Confidence: {ocr_result.confidence:.2f}")
            print(f"   Engine: {ocr_result.engine_used}")
            print(f"   Processing Time: {ocr_result.processing_time:.2f}s")
        else:
            print("❌ OCR Failed")
            
    except Exception as e:
        print(f"❌ OCR Error: {e}")
    
    # Example 2: Face Recognition Service
    print("\n2️⃣  Face Recognition")
    print("-" * 30)
    try:
        from face_recognition.face_service import FaceRecognitionService
        
        face_service = FaceRecognitionService()
        face_result = face_service.compare_faces(
            sample_image,  # document image
            sample_image   # selfie image
        )
        
        if face_result.success:
            match_status = "✅ Match" if face_result.is_match else "❌ No Match"
            print(f"{match_status} - Score: {face_result.match_score:.2f}")
            print(f"   Confidence: {face_result.confidence:.2f}")
            print(f"   Processing Time: {face_result.processing_time:.2f}s")
        else:
            print("❌ Face Recognition Failed")
            
    except Exception as e:
        print(f"❌ Face Recognition Error: {e}")
    
    # Example 3: Liveness Detection Service
    print("\n3️⃣  Liveness Detection")
    print("-" * 30)
    try:
        from liveness_detection.liveness_service import LivenessDetectionService
        
        liveness_service = LivenessDetectionService()
        liveness_result = liveness_service.detect_liveness(sample_image)
        
        if liveness_result.success:
            live_status = "✅ Live" if liveness_result.is_live else "❌ Not Live"
            print(f"{live_status} - Score: {liveness_result.liveness_score:.2f}")
            print(f"   Confidence: {liveness_result.confidence:.2f}")
            print(f"   Spoofing Attempts: {len(liveness_result.spoofing_attempts)}")
            print(f"   Processing Time: {liveness_result.processing_time:.2f}s")
        else:
            print("❌ Liveness Detection Failed")
            
    except Exception as e:
        print(f"❌ Liveness Detection Error: {e}")
    
    print("\n" + "=" * 50)


async def example_system_health():
    """
    Example of checking system health
    """
    print("\n🏥 System Health Check")
    print("=" * 50)
    
    try:
        health_status = await ai_verification_service.get_system_health()
        
        print("Service Status:")
        for service, status in health_status.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {service.replace('_', ' ').title()}: {'Healthy' if status else 'Unhealthy'}")
        
        # Overall system health
        all_healthy = all(health_status.values())
        overall_icon = "✅" if all_healthy else "❌"
        print(f"\n{overall_icon} Overall System Health: {'Good' if all_healthy else 'Issues Detected'}")
        
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
    
    print("\n" + "=" * 50)


async def main():
    """
    Main example function
    """
    print("🚀 AI Verification System - Comprehensive Examples")
    print("=" * 60)
    
    # Example 1: Comprehensive verification
    await example_verification()
    
    # Example 2: Individual services
    await example_individual_services()
    
    # Example 3: System health
    await example_system_health()
    
    print("\n🎉 All examples completed!")
    print("\nTo use this system in your application:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Configure environment variables in .env file")
    print("3. Import and use the ai_verification_service")
    print("\nSee README.md for detailed documentation.")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main()) 