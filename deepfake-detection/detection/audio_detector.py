"""
Audio Deepfake Detection Service
"""
import numpy as np
import librosa
import torch
import torch.nn as nn
import time
from typing import List, Dict, Optional, Any
from loguru import logger
import tempfile
import os

from ..models.schemas import (
    DetectionResult, AudioFeatures, AudioSegmentAnalysis,
    AuthenticityLevel, DetectionMethod
)
from ..utils.media_utils import MediaProcessor
from ..config.settings import settings, ThresholdConfig


class AudioDeepfakeDetector:
    """Audio deepfake detection service"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() and settings.use_gpu else 'cpu')
        self.audio_model = None
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize audio detection models"""
        try:
            # Simple LSTM-based audio deepfake detector
            self.audio_model = self._create_audio_model()
            logger.info("Audio deepfake detection model initialized")
            
        except Exception as e:
            logger.error(f"Error initializing audio models: {e}")
    
    def _create_audio_model(self) -> nn.Module:
        """Create audio deepfake detection model"""
        class AudioDeepfakeModel(nn.Module):
            def __init__(self, input_size=80, hidden_size=128, num_layers=2, num_classes=2):
                super(AudioDeepfakeModel, self).__init__()
                
                self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                                  batch_first=True, dropout=0.3)
                self.attention = nn.MultiheadAttention(hidden_size, num_heads=8)
                self.fc = nn.Sequential(
                    nn.Linear(hidden_size, 64),
                    nn.ReLU(),
                    nn.Dropout(0.3),
                    nn.Linear(64, num_classes)
                )
                
            def forward(self, x):
                # x shape: (batch_size, seq_len, features)
                lstm_out, _ = self.lstm(x)
                
                # Apply attention
                attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
                
                # Global average pooling
                pooled = torch.mean(attn_out, dim=1)
                
                # Classification
                output = self.fc(pooled)
                return output
        
        model = AudioDeepfakeModel().to(self.device)
        model.eval()
        return model
    
    def detect_deepfake_in_audio(self, audio_base64: str) -> DetectionResult:
        """Detect deepfake in audio"""
        start_time = time.time()
        
        try:
            # Extract audio segments
            segments = MediaProcessor.extract_audio_segments(
                audio_base64, 
                segment_duration=settings.audio_chunk_duration
            )
            
            if not segments:
                return self._create_no_audio_result(start_time)
            
            # Analyze each segment
            segment_results = []
            deepfake_probabilities = []
            
            for i, segment in enumerate(segments):
                # Extract features
                features = self._extract_audio_features(segment)
                
                # Run deepfake detection
                prob = self._run_audio_model(features)
                deepfake_probabilities.append(prob)
                
                # Create segment analysis
                segment_analysis = AudioSegmentAnalysis(
                    start_time=i * settings.audio_chunk_duration,
                    end_time=(i + 1) * settings.audio_chunk_duration,
                    deepfake_probability=prob,
                    authenticity_level=self._determine_authenticity_level(prob),
                    voice_features=features.__dict__ if hasattr(features, '__dict__') else {},
                    anomalies=self._detect_audio_anomalies(features)
                )
                segment_results.append(segment_analysis)
            
            # Combine results
            overall_probability = max(deepfake_probabilities) if deepfake_probabilities else 0.0
            combined_features = self._combine_audio_features(segments)
            
            # Determine authenticity and confidence
            authenticity_level = self._determine_authenticity_level(overall_probability)
            confidence = self._calculate_audio_confidence(overall_probability, combined_features)
            
            return DetectionResult(
                method=DetectionMethod.AUDIO_ANALYSIS,
                probability=float(overall_probability),
                confidence=float(confidence),
                authenticity_level=authenticity_level,
                processing_time=time.time() - start_time,
                features=combined_features
            )
            
        except Exception as e:
            logger.error(f"Error in audio deepfake detection: {e}")
            return self._create_error_result(start_time)
    
    def _extract_audio_features(self, audio_segment: np.ndarray) -> AudioFeatures:
        """Extract audio features for deepfake detection"""
        try:
            sr = settings.audio_sample_rate
            
            # Spectral features
            spectral_features = self._extract_spectral_features(audio_segment, sr)
            
            # Prosodic features
            prosodic_features = self._extract_prosodic_features(audio_segment, sr)
            
            # Voice biometrics
            voice_biometrics = self._extract_voice_biometrics(audio_segment, sr)
            
            # Breathing patterns
            breathing_patterns = self._analyze_breathing_patterns(audio_segment, sr)
            
            # Vocal tract features
            vocal_tract_features = self._extract_vocal_tract_features(audio_segment, sr)
            
            # Speech naturalness
            speech_naturalness = self._assess_speech_naturalness(audio_segment, sr)
            
            return AudioFeatures(
                spectral_features=spectral_features,
                prosodic_features=prosodic_features,
                voice_biometrics=voice_biometrics,
                breathing_patterns=breathing_patterns,
                vocal_tract_features=vocal_tract_features,
                speech_naturalness=speech_naturalness
            )
            
        except Exception as e:
            logger.error(f"Error extracting audio features: {e}")
            return self._default_audio_features()
    
    def _extract_spectral_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract spectral features"""
        try:
            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            mfcc_mean = np.mean(mfccs, axis=1)
            mfcc_std = np.std(mfccs, axis=1)
            
            # Spectral centroid
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            
            # Spectral rolloff
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio)[0]
            
            # Spectral bandwidth
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)[0]
            
            return {
                "mfcc_mean": float(np.mean(mfcc_mean)),
                "mfcc_std": float(np.mean(mfcc_std)),
                "spectral_centroid": float(np.mean(spectral_centroids)),
                "spectral_rolloff": float(np.mean(spectral_rolloff)),
                "zero_crossing_rate": float(np.mean(zcr)),
                "spectral_bandwidth": float(np.mean(spectral_bandwidth))
            }
            
        except Exception as e:
            logger.error(f"Error extracting spectral features: {e}")
            return {"error": str(e)}
    
    def _extract_prosodic_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract prosodic features"""
        try:
            # Fundamental frequency (F0)
            f0 = librosa.yin(audio, fmin=80, fmax=400)
            f0_mean = np.mean(f0[f0 > 0])
            f0_std = np.std(f0[f0 > 0])
            
            # Energy/RMS
            rms = librosa.feature.rms(y=audio)[0]
            energy_mean = float(np.mean(rms))
            energy_std = float(np.std(rms))
            
            # Tempo estimation
            tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
            
            return {
                "f0_mean": float(f0_mean) if not np.isnan(f0_mean) else 0.0,
                "f0_std": float(f0_std) if not np.isnan(f0_std) else 0.0,
                "energy_mean": energy_mean,
                "energy_std": energy_std,
                "tempo": float(tempo)
            }
            
        except Exception as e:
            logger.error(f"Error extracting prosodic features: {e}")
            return {"error": str(e)}
    
    def _extract_voice_biometrics(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract voice biometric features"""
        try:
            # Formant frequencies (simplified)
            # In practice, you'd use more sophisticated formant extraction
            stft = librosa.stft(audio)
            magnitude = np.abs(stft)
            
            # Estimate formants from spectral peaks
            freq_bins = librosa.fft_frequencies(sr=sr)
            formant_estimates = []
            
            for frame in magnitude.T:
                peaks = np.where(frame > np.mean(frame) + 2 * np.std(frame))[0]
                if len(peaks) >= 2:
                    formant_estimates.append(freq_bins[peaks[:2]])
            
            if formant_estimates:
                f1_mean = float(np.mean([f[0] for f in formant_estimates if len(f) > 0]))
                f2_mean = float(np.mean([f[1] for f in formant_estimates if len(f) > 1]))
            else:
                f1_mean = f2_mean = 0.0
            
            # Jitter and shimmer (simplified)
            jitter = float(np.std(np.diff(audio)) / np.mean(np.abs(audio))) if np.mean(np.abs(audio)) > 0 else 0.0
            shimmer = float(np.std(rms) / np.mean(rms)) if np.mean(rms) > 0 else 0.0
            
            return {
                "f1_mean": f1_mean,
                "f2_mean": f2_mean,
                "jitter": jitter,
                "shimmer": shimmer
            }
            
        except Exception as e:
            logger.error(f"Error extracting voice biometrics: {e}")
            return {"error": str(e)}
    
    def _analyze_breathing_patterns(self, audio: np.ndarray, sr: int) -> float:
        """Analyze breathing patterns"""
        try:
            # Detect low-frequency components that might indicate breathing
            # Apply low-pass filter to isolate breathing frequencies (0.1-1 Hz)
            from scipy import signal
            
            nyquist = sr / 2
            low_freq = 0.1 / nyquist
            high_freq = 1.0 / nyquist
            
            if high_freq < 1.0:
                b, a = signal.butter(4, [low_freq, high_freq], btype='band')
                breathing_signal = signal.filtfilt(b, a, audio)
                
                # Calculate breathing regularity
                breathing_energy = np.sum(breathing_signal ** 2)
                total_energy = np.sum(audio ** 2)
                
                breathing_ratio = breathing_energy / (total_energy + 1e-8)
                return float(min(1.0, breathing_ratio * 100))
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error analyzing breathing patterns: {e}")
            return 0.0
    
    def _extract_vocal_tract_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract vocal tract features"""
        try:
            # Linear Predictive Coding (LPC) coefficients
            # Simplified implementation
            from scipy import signal
            
            # Apply pre-emphasis
            pre_emphasis = 0.97
            emphasized = np.append(audio[0], audio[1:] - pre_emphasis * audio[:-1])
            
            # Calculate autocorrelation
            autocorr = np.correlate(emphasized, emphasized, mode='full')
            autocorr = autocorr[autocorr.size // 2:]
            
            # Extract first few coefficients as features
            lpc_order = min(12, len(autocorr) - 1)
            lpc_coeffs = autocorr[:lpc_order]
            
            return {
                f"lpc_{i}": float(coeff) for i, coeff in enumerate(lpc_coeffs)
            }
            
        except Exception as e:
            logger.error(f"Error extracting vocal tract features: {e}")
            return {"error": str(e)}
    
    def _assess_speech_naturalness(self, audio: np.ndarray, sr: int) -> float:
        """Assess speech naturalness"""
        try:
            # Calculate various naturalness indicators
            
            # Spectral flux (measure of spectral change)
            stft = librosa.stft(audio)
            magnitude = np.abs(stft)
            spectral_flux = np.mean(np.diff(magnitude, axis=1) ** 2)
            
            # Harmonicity (ratio of harmonic to noise components)
            harmonic, percussive = librosa.effects.hpss(audio)
            harmonic_ratio = np.sum(harmonic ** 2) / (np.sum(audio ** 2) + 1e-8)
            
            # Regularity of speech patterns
            tempo_consistency = self._calculate_tempo_consistency(audio, sr)
            
            # Combine indicators
            naturalness_score = (
                min(1.0, spectral_flux / 1000.0) * 0.3 +
                harmonic_ratio * 0.4 +
                tempo_consistency * 0.3
            )
            
            return float(naturalness_score)
            
        except Exception as e:
            logger.error(f"Error assessing speech naturalness: {e}")
            return 0.5
    
    def _calculate_tempo_consistency(self, audio: np.ndarray, sr: int) -> float:
        """Calculate tempo consistency"""
        try:
            # Split audio into segments and calculate tempo for each
            segment_length = sr * 2  # 2 seconds
            tempos = []
            
            for i in range(0, len(audio) - segment_length, segment_length // 2):
                segment = audio[i:i + segment_length]
                try:
                    tempo, _ = librosa.beat.beat_track(y=segment, sr=sr)
                    if tempo > 0:
                        tempos.append(tempo)
                except:
                    continue
            
            if len(tempos) > 1:
                # Calculate coefficient of variation (lower = more consistent)
                tempo_cv = np.std(tempos) / (np.mean(tempos) + 1e-8)
                consistency = max(0.0, 1.0 - tempo_cv)
                return float(consistency)
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"Error calculating tempo consistency: {e}")
            return 0.5
    
    def _run_audio_model(self, features: AudioFeatures) -> float:
        """Run audio deepfake detection model"""
        try:
            # Convert features to tensor format
            feature_vector = self._features_to_tensor(features)
            
            with torch.no_grad():
                output = self.audio_model(feature_vector)
                prob = torch.softmax(output, dim=1)[0, 1].cpu().item()
                return prob
                
        except Exception as e:
            logger.error(f"Error running audio model: {e}")
            return 0.5
    
    def _features_to_tensor(self, features: AudioFeatures) -> torch.Tensor:
        """Convert audio features to tensor format"""
        try:
            # Flatten all features into a single vector
            feature_list = []
            
            # Add spectral features
            for value in features.spectral_features.values():
                if isinstance(value, (int, float)) and not np.isnan(value):
                    feature_list.append(float(value))
            
            # Add prosodic features
            for value in features.prosodic_features.values():
                if isinstance(value, (int, float)) and not np.isnan(value):
                    feature_list.append(float(value))
            
            # Add voice biometrics
            for value in features.voice_biometrics.values():
                if isinstance(value, (int, float)) and not np.isnan(value):
                    feature_list.append(float(value))
            
            # Add other features
            feature_list.extend([
                features.breathing_patterns,
                features.speech_naturalness
            ])
            
            # Pad or truncate to expected size (80 features)
            expected_size = 80
            if len(feature_list) < expected_size:
                feature_list.extend([0.0] * (expected_size - len(feature_list)))
            else:
                feature_list = feature_list[:expected_size]
            
            # Convert to tensor and add batch and sequence dimensions
            tensor = torch.tensor(feature_list, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
            return tensor.to(self.device)
            
        except Exception as e:
            logger.error(f"Error converting features to tensor: {e}")
            return torch.zeros(1, 1, 80).to(self.device)
    
    def _detect_audio_anomalies(self, features: AudioFeatures) -> List[str]:
        """Detect anomalies in audio features"""
        anomalies = []
        
        try:
            # Check for unusual spectral characteristics
            if "mfcc_mean" in features.spectral_features:
                mfcc_mean = features.spectral_features["mfcc_mean"]
                if mfcc_mean < -50 or mfcc_mean > 50:
                    anomalies.append("Unusual MFCC characteristics")
            
            # Check for unnatural prosodic features
            if "f0_mean" in features.prosodic_features:
                f0_mean = features.prosodic_features["f0_mean"]
                if f0_mean < 80 or f0_mean > 400:
                    anomalies.append("Unusual fundamental frequency")
            
            # Check for breathing pattern anomalies
            if features.breathing_patterns > 0.8:
                anomalies.append("Unusual breathing patterns")
            
            # Check for speech naturalness
            if features.speech_naturalness < 0.3:
                anomalies.append("Unnatural speech patterns")
            
        except Exception as e:
            logger.error(f"Error detecting audio anomalies: {e}")
        
        return anomalies
    
    def _combine_audio_features(self, segments: List[np.ndarray]) -> AudioFeatures:
        """Combine audio features from multiple segments"""
        try:
            if not segments:
                return self._default_audio_features()
            
            # Extract features from all segments
            all_features = [self._extract_audio_features(segment) for segment in segments]
            
            # Average the features
            combined_spectral = {}
            combined_prosodic = {}
            combined_biometrics = {}
            
            # Average spectral features
            for feature_set in all_features:
                for key, value in feature_set.spectral_features.items():
                    if isinstance(value, (int, float)):
                        if key not in combined_spectral:
                            combined_spectral[key] = []
                        combined_spectral[key].append(value)
            
            for key in combined_spectral:
                combined_spectral[key] = float(np.mean(combined_spectral[key]))
            
            # Similar for other feature types
            for feature_set in all_features:
                for key, value in feature_set.prosodic_features.items():
                    if isinstance(value, (int, float)):
                        if key not in combined_prosodic:
                            combined_prosodic[key] = []
                        combined_prosodic[key].append(value)
            
            for key in combined_prosodic:
                combined_prosodic[key] = float(np.mean(combined_prosodic[key]))
            
            for feature_set in all_features:
                for key, value in feature_set.voice_biometrics.items():
                    if isinstance(value, (int, float)):
                        if key not in combined_biometrics:
                            combined_biometrics[key] = []
                        combined_biometrics[key].append(value)
            
            for key in combined_biometrics:
                combined_biometrics[key] = float(np.mean(combined_biometrics[key]))
            
            # Average other features
            breathing_patterns = float(np.mean([f.breathing_patterns for f in all_features]))
            speech_naturalness = float(np.mean([f.speech_naturalness for f in all_features]))
            
            # Average vocal tract features
            combined_vocal_tract = {}
            for feature_set in all_features:
                for key, value in feature_set.vocal_tract_features.items():
                    if isinstance(value, (int, float)):
                        if key not in combined_vocal_tract:
                            combined_vocal_tract[key] = []
                        combined_vocal_tract[key].append(value)
            
            for key in combined_vocal_tract:
                combined_vocal_tract[key] = float(np.mean(combined_vocal_tract[key]))
            
            return AudioFeatures(
                spectral_features=combined_spectral,
                prosodic_features=combined_prosodic,
                voice_biometrics=combined_biometrics,
                breathing_patterns=breathing_patterns,
                vocal_tract_features=combined_vocal_tract,
                speech_naturalness=speech_naturalness
            )
            
        except Exception as e:
            logger.error(f"Error combining audio features: {e}")
            return self._default_audio_features()
    
    def _determine_authenticity_level(self, probability: float) -> AuthenticityLevel:
        """Determine authenticity level from probability"""
        if probability >= ThresholdConfig.HIGH_CONFIDENCE_THRESHOLD:
            return AuthenticityLevel.DEEPFAKE
        elif probability >= ThresholdConfig.AUDIO_DEEPFAKE_THRESHOLD:
            return AuthenticityLevel.LIKELY_FAKE
        elif probability >= ThresholdConfig.LOW_CONFIDENCE_THRESHOLD:
            return AuthenticityLevel.SUSPICIOUS
        else:
            return AuthenticityLevel.LIKELY_AUTHENTIC
    
    def _calculate_audio_confidence(self, probability: float, features: AudioFeatures) -> float:
        """Calculate confidence in audio detection"""
        try:
            base_confidence = abs(probability - 0.5) * 2
            
            # Feature consistency indicators
            naturalness_score = features.speech_naturalness
            breathing_score = 1.0 - min(1.0, features.breathing_patterns)
            
            feature_confidence = (naturalness_score + breathing_score) / 2.0
            
            return float(min(1.0, max(0.0, (base_confidence + feature_confidence) / 2.0)))
            
        except Exception as e:
            logger.error(f"Error calculating audio confidence: {e}")
            return 0.5
    
    def _default_audio_features(self) -> AudioFeatures:
        """Create default audio features"""
        return AudioFeatures(
            spectral_features={},
            prosodic_features={},
            voice_biometrics={},
            breathing_patterns=0.0,
            vocal_tract_features={},
            speech_naturalness=0.5
        )
    
    def _create_no_audio_result(self, start_time: float) -> DetectionResult:
        """Create result when no audio segments found"""
        return DetectionResult(
            method=DetectionMethod.AUDIO_ANALYSIS,
            probability=0.0,
            confidence=0.0,
            authenticity_level=AuthenticityLevel.AUTHENTIC,
            processing_time=time.time() - start_time,
            features=self._default_audio_features()
        )
    
    def _create_error_result(self, start_time: float) -> DetectionResult:
        """Create result on error"""
        return DetectionResult(
            method=DetectionMethod.AUDIO_ANALYSIS,
            probability=0.5,
            confidence=0.0,
            authenticity_level=AuthenticityLevel.SUSPICIOUS,
            processing_time=time.time() - start_time,
            features=self._default_audio_features()
        ) 