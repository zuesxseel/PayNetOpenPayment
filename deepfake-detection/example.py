#!/usr/bin/env python3
"""
Example script demonstrating deepfake detection system usage
"""
import asyncio
import base64
import time
from pathlib import Path

from main import deepfake_detector
from models.schemas import (
    DeepfakeDetectionRequest, MediaType, DetectionMethod,
    DeepfakeType, AuthenticityLevel, ProcessingStatus
)


async def example_image_detection():
    """Example of image deepfake detection"""
    print("=== Image Deepfake Detection Example ===")
    
    # Create a simple test image (1x1 pixel PNG)
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    def progress_callback(progress):
        print(f"Progress: {progress.progress:>3.0f}% - {progress.current_step}")
    
    try:
        # Create detection request
        request = DeepfakeDetectionRequest(
            media_data=test_image_base64,
            media_type=MediaType.IMAGE,
            detection_methods=[DetectionMethod.VISUAL_ANALYSIS],
            options={
                "high_accuracy": True,
                "include_features": True
            }
        )
        
        print(f"Analyzing image ({len(test_image_base64)} bytes)...")
        start_time = time.time()
        
        # Perform detection
        result = await deepfake_detector.detect_deepfake(request, progress_callback)
        
        # Display results
        print(f"\n--- Detection Results ---")
        print(f"Detection ID: {result.detection_id}")
        print(f"Media Type: {result.media_info.file_type}")
        print(f"File Size: {result.media_info.file_size} bytes")
        print(f"Resolution: {result.media_info.resolution}")
        print(f"")
        print(f"Is Deepfake: {result.is_deepfake}")
        print(f"Overall Probability: {result.overall_probability:.3f}")
        print(f"Confidence Score: {result.confidence_score:.3f}")
        print(f"Authenticity Level: {result.authenticity_level}")
        print(f"Processing Time: {result.total_processing_time:.3f}s")
        
        if result.detected_techniques:
            print(f"Detected Techniques: {', '.join([t.value for t in result.detected_techniques])}")
        
        if result.evidence:
            print(f"Evidence Found:")
            for evidence in result.evidence:
                print(f"  • {evidence}")
        
        if result.artifacts:
            print(f"Artifacts Detected: {', '.join(result.artifacts)}")
        
        if result.anomalies:
            print(f"Anomalies:")
            for anomaly in result.anomalies:
                print(f"  • {anomaly}")
        
        # Visual analysis details
        if result.visual_analysis:
            print(f"\n--- Visual Analysis Details ---")
            print(f"Method: {result.visual_analysis.method}")
            print(f"Probability: {result.visual_analysis.probability:.3f}")
            print(f"Confidence: {result.visual_analysis.confidence:.3f}")
            print(f"Authenticity: {result.visual_analysis.authenticity_level}")
            
            if result.visual_analysis.features:
                print(f"Visual Features:")
                features = result.visual_analysis.features
                if hasattr(features, 'texture_inconsistency'):
                    print(f"  • Texture Inconsistency: {features.texture_inconsistency:.3f}")
                if hasattr(features, 'frequency_artifacts'):
                    print(f"  • Frequency Artifacts: {features.frequency_artifacts:.3f}")
                if hasattr(features, 'lighting_consistency'):
                    print(f"  • Lighting Consistency: {features.lighting_consistency:.3f}")
                if hasattr(features, 'compression_artifacts'):
                    print(f"  • Compression Artifacts: {features.compression_artifacts:.3f}")
        
        print(f"\nTotal execution time: {time.time() - start_time:.3f}s")
        
    except Exception as e:
        print(f"Error during detection: {e}")


async def example_batch_detection():
    """Example of batch detection on multiple items"""
    print("\n=== Batch Detection Example ===")
    
    # Create multiple test images
    test_images = [
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGA4tZS1AAAAABJRU5ErkJggg=="
    ]
    
    print(f"Processing {len(test_images)} images...")
    
    results = []
    total_start_time = time.time()
    
    for i, image_data in enumerate(test_images, 1):
        print(f"\nProcessing image {i}/{len(test_images)}...")
        
        def progress_callback(progress):
            print(f"  {progress.progress:>3.0f}% - {progress.current_step}")
        
        try:
            request = DeepfakeDetectionRequest(
                media_data=image_data,
                media_type=MediaType.IMAGE,
                detection_methods=[DetectionMethod.VISUAL_ANALYSIS],
                options={"fast_mode": True}
            )
            
            result = await deepfake_detector.detect_deepfake(request, progress_callback)
            results.append(result)
            
            print(f"  Result: {result.authenticity_level} (prob: {result.overall_probability:.3f})")
            
        except Exception as e:
            print(f"  Error: {e}")
            results.append(None)
    
    # Summary
    print(f"\n--- Batch Results Summary ---")
    valid_results = [r for r in results if r is not None]
    
    if valid_results:
        deepfakes_detected = sum(1 for r in valid_results if r.is_deepfake)
        avg_probability = sum(r.overall_probability for r in valid_results) / len(valid_results)
        avg_confidence = sum(r.confidence_score for r in valid_results) / len(valid_results)
        avg_processing_time = sum(r.total_processing_time for r in valid_results) / len(valid_results)
        
        print(f"Total Images Processed: {len(valid_results)}")
        print(f"Deepfakes Detected: {deepfakes_detected}")
        print(f"Detection Rate: {deepfakes_detected/len(valid_results)*100:.1f}%")
        print(f"Average Probability: {avg_probability:.3f}")
        print(f"Average Confidence: {avg_confidence:.3f}")
        print(f"Average Processing Time: {avg_processing_time:.3f}s")
        print(f"Total Batch Time: {time.time() - total_start_time:.3f}s")
    else:
        print("No valid results obtained")


async def example_system_health():
    """Example of system health check"""
    print("\n=== System Health Check ===")
    
    try:
        health = await deepfake_detector.get_system_health()
        
        print("System Status:")
        for component, status in health.items():
            if isinstance(status, bool):
                status_str = "✓ OK" if status else "✗ FAILED"
            else:
                status_str = str(status)
            print(f"  {component}: {status_str}")
            
    except Exception as e:
        print(f"Error checking system health: {e}")


async def example_different_media_types():
    """Example showing different media type handling"""
    print("\n=== Different Media Types Example ===")
    
    # Test with different media types
    test_cases = [
        {
            "name": "Tiny PNG Image",
            "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
            "type": MediaType.IMAGE,
            "methods": [DetectionMethod.VISUAL_ANALYSIS]
        },
        # Note: For real usage, you would provide actual video/audio base64 data
        # These are just examples showing the structure
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        
        try:
            request = DeepfakeDetectionRequest(
                media_data=test_case["data"],
                media_type=test_case["type"],
                detection_methods=test_case["methods"],
                options={"quick_scan": True}
            )
            
            result = await deepfake_detector.detect_deepfake(request)
            
            print(f"  Media Type: {result.media_info.file_type}")
            print(f"  File Size: {result.media_info.file_size} bytes")
            print(f"  Authenticity: {result.authenticity_level}")
            print(f"  Processing Time: {result.total_processing_time:.3f}s")
            
        except Exception as e:
            print(f"  Error: {e}")


async def example_configuration_demo():
    """Example showing configuration options"""
    print("\n=== Configuration Example ===")
    
    from config.settings import settings, ThresholdConfig
    
    # Display current configuration
    print("Current Configuration:")
    print(f"  Deepfake Threshold: {settings.deepfake_threshold}")
    print(f"  Use GPU: {settings.use_gpu}")
    print(f"  Batch Size: {settings.batch_size}")
    print(f"  Max Frames per Video: {settings.max_frames_per_video}")
    print(f"  Audio Sample Rate: {settings.audio_sample_rate}")
    
    print("\nThreshold Configuration:")
    print(f"  High Confidence Threshold: {ThresholdConfig.HIGH_CONFIDENCE_THRESHOLD}")
    print(f"  Face Quality Minimum: {ThresholdConfig.FACE_QUALITY_MIN}")
    print(f"  Audio Deepfake Threshold: {ThresholdConfig.AUDIO_DEEPFAKE_THRESHOLD}")


async def main():
    """Main example function"""
    print("🔍 Deepfake Detection System - Example Usage")
    print("=" * 50)
    
    # Run all examples
    await example_image_detection()
    await example_batch_detection()
    await example_system_health()
    await example_different_media_types()
    await example_configuration_demo()
    
    print("\n" + "=" * 50)
    print("✅ All examples completed successfully!")
    print("\nFor real usage:")
    print("1. Replace test data with actual image/video/audio files")
    print("2. Configure thresholds based on your requirements")
    print("3. Implement proper error handling for production use")
    print("4. Consider using batch processing for multiple files")
    print("5. Monitor system resources and performance")


if __name__ == "__main__":
    asyncio.run(main()) 