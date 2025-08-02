"""
Audio Preprocessing Module for Deepfake Detection
Handles audio feature extraction, normalization, and segmentation
"""
import numpy as np
import librosa
import torch
import torchaudio
from typing import List, Tuple, Optional, Dict, Any, Union
from loguru import logger
import scipy.signal
from scipy.fft import fft, ifft
import tempfile
import os

from ..models.schemas import AudioFeatures
from ..config.settings import settings


class AudioPreprocessor:
    """Handles all audio preprocessing tasks for deepfake detection"""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.n_fft = 2048
        self.hop_length = 512
        self.n_mels = 128
        self.n_mfcc = 13
        
        # Mel filterbank for spectral features
        self.mel_filters = librosa.filters.mel(
            sr=self.sample_rate,
            n_fft=self.n_fft,
            n_mels=self.n_mels
        )
        
        logger.info(f"Audio Preprocessor initialized with sample rate: {self.sample_rate} Hz")
    
    def preprocess_audio(
        self,
        audio: np.ndarray,
        target_length: Optional[int] = None,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Preprocess audio signal for deepfake detection
        
        Args:
            audio: Input audio signal
            target_length: Target length in samples (if None, keep original)
            normalize: Whether to normalize the audio
            
        Returns:
            Preprocessed audio signal
        """
        try:
            # Ensure audio is 1D
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)
            
            # Remove DC component
            audio = audio - np.mean(audio)
            
            # Normalize audio
            if normalize:
                audio = self._normalize_audio(audio)
            
            # Apply pre-emphasis filter
            audio = self._apply_preemphasis(audio)
            
            # Resample if needed
            if target_length is not None:
                audio = self._resize_audio(audio, target_length)
            
            return audio
            
        except Exception as e:
            logger.error(f"Error preprocessing audio: {e}")
            return audio
    
    def extract_features(
        self,
        audio: np.ndarray,
        feature_types: List[str] = None
    ) -> Dict[str, np.ndarray]:
        """
        Extract comprehensive audio features for deepfake detection
        
        Args:
            audio: Input audio signal
            feature_types: List of feature types to extract
            
        Returns:
            Dictionary of extracted features
        """
        if feature_types is None:
            feature_types = ['mfcc', 'spectral', 'prosodic', 'temporal']
        
        features = {}
        
        try:
            # Spectral features
            if 'spectral' in feature_types:
                features.update(self._extract_spectral_features(audio))
            
            # MFCC features
            if 'mfcc' in feature_types:
                features.update(self._extract_mfcc_features(audio))
            
            # Prosodic features
            if 'prosodic' in feature_types:
                features.update(self._extract_prosodic_features(audio))
            
            # Temporal features
            if 'temporal' in feature_types:
                features.update(self._extract_temporal_features(audio))
            
            # Voice quality features
            if 'voice_quality' in feature_types:
                features.update(self._extract_voice_quality_features(audio))
            
            # Frequency domain features
            if 'frequency' in feature_types:
                features.update(self._extract_frequency_features(audio))
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting audio features: {e}")
            return {}
    
    def segment_audio(
        self,
        audio: np.ndarray,
        segment_length: float = 3.0,
        overlap: float = 0.5
    ) -> List[np.ndarray]:
        """
        Segment audio into fixed-length chunks with overlap
        
        Args:
            audio: Input audio signal
            segment_length: Length of each segment in seconds
            overlap: Overlap ratio between segments
            
        Returns:
            List of audio segments
        """
        try:
            segment_samples = int(segment_length * self.sample_rate)
            hop_samples = int(segment_samples * (1 - overlap))
            
            segments = []
            start = 0
            
            while start + segment_samples <= len(audio):
                segment = audio[start:start + segment_samples]
                segments.append(segment)
                start += hop_samples
            
            # Add last segment if there's remaining audio
            if start < len(audio):
                remaining = audio[start:]
                # Pad with zeros to reach target length
                if len(remaining) < segment_samples:
                    padded = np.zeros(segment_samples)
                    padded[:len(remaining)] = remaining
                    segments.append(padded)
            
            return segments
            
        except Exception as e:
            logger.error(f"Error segmenting audio: {e}")
            return [audio]
    
    def detect_voice_activity(
        self,
        audio: np.ndarray,
        threshold: float = 0.01,
        frame_length: int = 2048,
        hop_length: int = 512
    ) -> np.ndarray:
        """
        Detect voice activity in audio signal
        
        Args:
            audio: Input audio signal
            threshold: Energy threshold for voice detection
            frame_length: Frame length for analysis
            hop_length: Hop length between frames
            
        Returns:
            Boolean array indicating voice activity
        """
        try:
            # Calculate frame energy
            frames = librosa.util.frame(audio, frame_length=frame_length, 
                                      hop_length=hop_length, axis=0)
            energy = np.sum(frames ** 2, axis=0)
            
            # Normalize energy
            energy = energy / np.max(energy + 1e-8)
            
            # Apply threshold
            voice_activity = energy > threshold
            
            return voice_activity
            
        except Exception as e:
            logger.error(f"Error detecting voice activity: {e}")
            return np.ones(len(audio) // hop_length, dtype=bool)
    
    def remove_silence(
        self,
        audio: np.ndarray,
        top_db: int = 20
    ) -> np.ndarray:
        """
        Remove silent parts from audio
        
        Args:
            audio: Input audio signal
            top_db: Threshold for silence detection
            
        Returns:
            Audio with silence removed
        """
        try:
            # Use librosa's trim function
            trimmed_audio, _ = librosa.effects.trim(audio, top_db=top_db)
            return trimmed_audio
            
        except Exception as e:
            logger.error(f"Error removing silence: {e}")
            return audio
    
    def apply_noise_reduction(
        self,
        audio: np.ndarray,
        noise_factor: float = 0.1
    ) -> np.ndarray:
        """
        Apply noise reduction to audio signal
        
        Args:
            audio: Input audio signal
            noise_factor: Factor for noise reduction
            
        Returns:
            Denoised audio signal
        """
        try:
            # Simple spectral subtraction
            stft = librosa.stft(audio, n_fft=self.n_fft, hop_length=self.hop_length)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise floor
            noise_floor = np.percentile(magnitude, 10, axis=1, keepdims=True)
            
            # Spectral subtraction
            magnitude_denoised = magnitude - noise_factor * noise_floor
            magnitude_denoised = np.maximum(magnitude_denoised, 
                                          magnitude * (1 - noise_factor))
            
            # Reconstruct signal
            stft_denoised = magnitude_denoised * np.exp(1j * phase)
            audio_denoised = librosa.istft(stft_denoised, hop_length=self.hop_length)
            
            return audio_denoised
            
        except Exception as e:
            logger.error(f"Error applying noise reduction: {e}")
            return audio
    
    def _extract_spectral_features(self, audio: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract spectral features from audio"""
        features = {}
        
        try:
            # Compute spectogram
            stft = librosa.stft(audio, n_fft=self.n_fft, hop_length=self.hop_length)
            magnitude = np.abs(stft)
            
            # Spectral centroid
            features['spectral_centroid'] = librosa.feature.spectral_centroid(
                S=magnitude, sr=self.sample_rate
            )[0]
            
            # Spectral rolloff
            features['spectral_rolloff'] = librosa.feature.spectral_rolloff(
                S=magnitude, sr=self.sample_rate
            )[0]
            
            # Spectral bandwidth
            features['spectral_bandwidth'] = librosa.feature.spectral_bandwidth(
                S=magnitude, sr=self.sample_rate
            )[0]
            
            # Zero crossing rate
            features['zero_crossing_rate'] = librosa.feature.zero_crossing_rate(audio)[0]
            
            # Spectral contrast
            features['spectral_contrast'] = librosa.feature.spectral_contrast(
                S=magnitude, sr=self.sample_rate
            )
            
            # Spectral flatness
            features['spectral_flatness'] = librosa.feature.spectral_flatness(S=magnitude)[0]
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting spectral features: {e}")
            return {}
    
    def _extract_mfcc_features(self, audio: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract MFCC features from audio"""
        features = {}
        
        try:
            # MFCC coefficients
            mfcc = librosa.feature.mfcc(
                y=audio, sr=self.sample_rate, n_mfcc=self.n_mfcc,
                n_fft=self.n_fft, hop_length=self.hop_length
            )
            features['mfcc'] = mfcc
            
            # Delta and delta-delta features
            features['mfcc_delta'] = librosa.feature.delta(mfcc)
            features['mfcc_delta2'] = librosa.feature.delta(mfcc, order=2)
            
            # Mel spectrogram
            mel_spec = librosa.feature.melspectrogram(
                y=audio, sr=self.sample_rate, n_mels=self.n_mels,
                n_fft=self.n_fft, hop_length=self.hop_length
            )
            features['mel_spectrogram'] = librosa.power_to_db(mel_spec)
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting MFCC features: {e}")
            return {}
    
    def _extract_prosodic_features(self, audio: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract prosodic features (F0, energy, etc.)"""
        features = {}
        
        try:
            # Fundamental frequency (F0)
            f0, voiced_flag, voiced_probs = librosa.pyin(
                audio, fmin=librosa.note_to_hz('C2'),
                fmax=librosa.note_to_hz('C7'), sr=self.sample_rate
            )
            features['f0'] = f0
            features['voiced_flag'] = voiced_flag.astype(float)
            features['voiced_probs'] = voiced_probs
            
            # Energy (RMS)
            features['rms_energy'] = librosa.feature.rms(
                y=audio, frame_length=self.n_fft, hop_length=self.hop_length
            )[0]
            
            # Tempo and beat tracking
            tempo, beats = librosa.beat.beat_track(y=audio, sr=self.sample_rate)
            features['tempo'] = np.array([tempo])
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting prosodic features: {e}")
            return {}
    
    def _extract_temporal_features(self, audio: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract temporal features from audio"""
        features = {}
        
        try:
            # Signal statistics
            features['mean'] = np.array([np.mean(audio)])
            features['std'] = np.array([np.std(audio)])
            features['skewness'] = np.array([scipy.stats.skew(audio)])
            features['kurtosis'] = np.array([scipy.stats.kurtosis(audio)])
            
            # Signal energy
            features['total_energy'] = np.array([np.sum(audio ** 2)])
            
            # Duration features
            features['duration'] = np.array([len(audio) / self.sample_rate])
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting temporal features: {e}")
            return {}
    
    def _extract_voice_quality_features(self, audio: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract voice quality features"""
        features = {}
        
        try:
            # Jitter and shimmer (simplified calculation)
            f0, _, _ = librosa.pyin(audio, fmin=50, fmax=500, sr=self.sample_rate)
            f0_clean = f0[~np.isnan(f0)]
            
            if len(f0_clean) > 1:
                # Jitter (F0 variation)
                f0_diff = np.diff(f0_clean)
                jitter = np.std(f0_diff) / np.mean(f0_clean) if np.mean(f0_clean) > 0 else 0
                features['jitter'] = np.array([jitter])
                
                # Shimmer (amplitude variation)
                rms = librosa.feature.rms(y=audio, hop_length=self.hop_length)[0]
                rms_clean = rms[rms > 0]
                if len(rms_clean) > 1:
                    rms_diff = np.diff(rms_clean)
                    shimmer = np.std(rms_diff) / np.mean(rms_clean)
                    features['shimmer'] = np.array([shimmer])
            
            # Harmonic-to-noise ratio
            harmonic, percussive = librosa.effects.hpss(audio)
            hnr = np.mean(harmonic ** 2) / (np.mean(percussive ** 2) + 1e-8)
            features['hnr'] = np.array([hnr])
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting voice quality features: {e}")
            return {}
    
    def _extract_frequency_features(self, audio: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract frequency domain features"""
        features = {}
        
        try:
            # FFT
            fft_values = np.abs(fft(audio))
            fft_freqs = np.fft.fftfreq(len(audio), 1/self.sample_rate)
            
            # Only use positive frequencies
            n_positive = len(fft_values) // 2
            fft_values = fft_values[:n_positive]
            fft_freqs = fft_freqs[:n_positive]
            
            # Spectral peak
            peak_idx = np.argmax(fft_values)
            features['spectral_peak_freq'] = np.array([fft_freqs[peak_idx]])
            features['spectral_peak_magnitude'] = np.array([fft_values[peak_idx]])
            
            # Spectral spread
            centroid = np.sum(fft_freqs * fft_values) / np.sum(fft_values)
            spread = np.sqrt(np.sum(((fft_freqs - centroid) ** 2) * fft_values) / np.sum(fft_values))
            features['spectral_spread'] = np.array([spread])
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting frequency features: {e}")
            return {}
    
    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio signal"""
        try:
            # RMS normalization
            rms = np.sqrt(np.mean(audio ** 2))
            if rms > 0:
                audio = audio / rms * 0.1  # Target RMS of 0.1
            
            # Peak normalization as fallback
            peak = np.max(np.abs(audio))
            if peak > 1.0:
                audio = audio / peak * 0.95
            
            return audio
            
        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            return audio
    
    def _apply_preemphasis(self, audio: np.ndarray, coeff: float = 0.97) -> np.ndarray:
        """Apply pre-emphasis filter to audio"""
        try:
            return np.append(audio[0], audio[1:] - coeff * audio[:-1])
        except Exception as e:
            logger.error(f"Error applying pre-emphasis: {e}")
            return audio
    
    def _resize_audio(self, audio: np.ndarray, target_length: int) -> np.ndarray:
        """Resize audio to target length"""
        try:
            current_length = len(audio)
            
            if current_length == target_length:
                return audio
            elif current_length < target_length:
                # Pad with zeros
                padded = np.zeros(target_length)
                padded[:current_length] = audio
                return padded
            else:
                # Truncate or resample
                return audio[:target_length]
                
        except Exception as e:
            logger.error(f"Error resizing audio: {e}")
            return audio
    
    def create_feature_matrix(
        self,
        features_dict: Dict[str, np.ndarray],
        flatten: bool = True
    ) -> np.ndarray:
        """
        Create feature matrix from extracted features
        
        Args:
            features_dict: Dictionary of features
            flatten: Whether to flatten 2D features
            
        Returns:
            Feature matrix
        """
        try:
            feature_list = []
            
            for key, feature in features_dict.items():
                if feature.ndim == 1:
                    feature_list.append(feature)
                elif feature.ndim == 2:
                    if flatten:
                        # Flatten 2D features
                        feature_list.append(feature.flatten())
                    else:
                        # Use statistical summaries
                        feature_list.append(np.mean(feature, axis=1))
                        feature_list.append(np.std(feature, axis=1))
                        feature_list.append(np.max(feature, axis=1))
                        feature_list.append(np.min(feature, axis=1))
            
            if feature_list:
                return np.concatenate(feature_list)
            else:
                return np.array([])
                
        except Exception as e:
            logger.error(f"Error creating feature matrix: {e}")
            return np.array([]) 