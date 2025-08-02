"""
UEBA Behavior Analytics Engine
Core component for analyzing user and entity behavior patterns
"""
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from loguru import logger
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import networkx as nx

from ..models.schemas import (
    Entity, User, Device, Application, BaseEvent, AuthenticationEvent,
    DataAccessEvent, NetworkAccessEvent, BehaviorBaseline, AnomalyDetection,
    RiskScore, EntityType, EventType, AnomalyType, RiskLevel, Alert,
    AlertSeverity, UserBehaviorAnalysis, EntityRelationship, FeatureVector,
    BehaviorProfile
)
from ..config.settings import settings, AnalyticsConfig
from ..utils.time_utils import TimeAnalyzer
from ..utils.geo_utils import GeoAnalyzer


class BehaviorEngine:
    """Core behavior analytics engine"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.baselines = {}
        self.entity_profiles = {}
        self.time_analyzer = TimeAnalyzer()
        self.geo_analyzer = GeoAnalyzer()
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize ML models for anomaly detection"""
        try:
            # Isolation Forest for general anomaly detection
            self.models['isolation_forest'] = IsolationForest(
                **AnalyticsConfig.ANOMALY_MODELS['isolation_forest']
            )
            
            # Local Outlier Factor for density-based anomalies
            self.models['local_outlier_factor'] = LocalOutlierFactor(
                **AnalyticsConfig.ANOMALY_MODELS['local_outlier_factor']
            )
            
            # One-Class SVM for pattern-based anomalies
            self.models['one_class_svm'] = OneClassSVM(
                **AnalyticsConfig.ANOMALY_MODELS['one_class_svm']
            )
            
            # Standard scaler for feature normalization
            self.scalers['standard'] = StandardScaler()
            
            logger.info("Behavior analytics models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing behavior models: {e}")
    
    async def analyze_entity_behavior(
        self,
        entity: Entity,
        events: List[BaseEvent],
        time_window_hours: int = 24
    ) -> UserBehaviorAnalysis:
        """
        Analyze behavior patterns for an entity
        
        Args:
            entity: Entity to analyze
            events: List of events for the entity
            time_window_hours: Time window for analysis
            
        Returns:
            Comprehensive behavior analysis
        """
        try:
            logger.info(f"Starting behavior analysis for entity {entity.entity_id}")
            
            # Filter events by time window
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            recent_events = [e for e in events if e.timestamp >= cutoff_time]
            
            if not recent_events:
                logger.warning(f"No recent events found for entity {entity.entity_id}")
                return self._create_empty_analysis(entity, time_window_hours)
            
            # Extract features from events
            features = await self._extract_behavioral_features(entity, recent_events)
            
            # Perform temporal analysis
            temporal_patterns = await self._analyze_temporal_patterns(recent_events)
            
            # Analyze access patterns
            access_patterns = await self._analyze_access_patterns(recent_events)
            
            # Geographic analysis
            geographic_patterns = await self._analyze_geographic_patterns(recent_events)
            
            # Detect anomalies
            anomalies = await self._detect_anomalies(entity, features, recent_events)
            
            # Identify risk indicators
            risk_indicators = await self._identify_risk_indicators(entity, recent_events, anomalies)
            
            # Detect behavioral changes
            behavioral_changes = await self._detect_behavioral_changes(entity, features)
            
            # Create activity summary
            activity_summary = self._create_activity_summary(recent_events)
            
            analysis = UserBehaviorAnalysis(
                user_id=entity.entity_id,
                analysis_period_start=cutoff_time,
                analysis_period_end=datetime.utcnow(),
                activity_summary=activity_summary,
                login_patterns=temporal_patterns.get('login_patterns', {}),
                access_patterns=access_patterns,
                geographic_patterns=geographic_patterns,
                temporal_patterns=temporal_patterns,
                anomalies_detected=[a.id for a in anomalies],
                risk_indicators=risk_indicators,
                behavioral_changes=behavioral_changes
            )
            
            logger.info(f"Behavior analysis completed for entity {entity.entity_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing entity behavior: {e}")
            return self._create_empty_analysis(entity, time_window_hours)
    
    async def _extract_behavioral_features(
        self,
        entity: Entity,
        events: List[BaseEvent]
    ) -> FeatureVector:
        """Extract behavioral features from events"""
        try:
            features = {}
            
            # Time-based features
            features.update(await self._extract_temporal_features(events))
            
            # Access-based features
            features.update(await self._extract_access_features(events))
            
            # Volume-based features
            features.update(await self._extract_volume_features(events))
            
            # Pattern-based features
            features.update(await self._extract_pattern_features(events))
            
            # Geographic features
            features.update(await self._extract_geographic_features(events))
            
            # Authentication-specific features
            auth_events = [e for e in events if isinstance(e, AuthenticationEvent)]
            if auth_events:
                features.update(await self._extract_auth_features(auth_events))
            
            return FeatureVector(
                entity_id=entity.entity_id,
                timestamp=datetime.utcnow(),
                features=features,
                window_size=f"{settings.ml_feature_window_hours}h"
            )
            
        except Exception as e:
            logger.error(f"Error extracting behavioral features: {e}")
            return FeatureVector(
                entity_id=entity.entity_id,
                timestamp=datetime.utcnow(),
                features={}
            )
    
    async def _extract_temporal_features(self, events: List[BaseEvent]) -> Dict[str, float]:
        """Extract time-based behavioral features"""
        if not events:
            return {}
        
        timestamps = [e.timestamp for e in events]
        
        # Convert to hours of day
        hours = [t.hour for t in timestamps]
        days_of_week = [t.weekday() for t in timestamps]
        
        # Calculate temporal statistics
        features = {
            'avg_hour_of_day': float(np.mean(hours)),
            'std_hour_of_day': float(np.std(hours)),
            'most_common_hour': float(max(set(hours), key=hours.count)),
            'avg_day_of_week': float(np.mean(days_of_week)),
            'weekend_activity_ratio': sum(1 for d in days_of_week if d >= 5) / len(days_of_week),
            'night_activity_ratio': sum(1 for h in hours if h < 6 or h > 22) / len(hours),
            'business_hours_ratio': sum(1 for h in hours if 9 <= h <= 17) / len(hours)
        }
        
        # Activity frequency features
        event_intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds() / 3600  # hours
            event_intervals.append(interval)
        
        if event_intervals:
            features.update({
                'avg_time_between_events': float(np.mean(event_intervals)),
                'std_time_between_events': float(np.std(event_intervals)),
                'max_idle_time': float(max(event_intervals)),
                'min_idle_time': float(min(event_intervals))
            })
        
        return features
    
    async def _extract_access_features(self, events: List[BaseEvent]) -> Dict[str, float]:
        """Extract access pattern features"""
        if not events:
            return {}
        
        # Categorize events by type
        event_types = [e.event_type for e in events]
        event_type_counts = {et.value: event_types.count(et) for et in EventType}
        
        total_events = len(events)
        features = {}
        
        # Event type distribution
        for event_type, count in event_type_counts.items():
            features[f'{event_type}_ratio'] = count / total_events
        
        # Access diversity
        unique_sources = set()
        unique_destinations = set()
        
        for event in events:
            if hasattr(event, 'source_ip') and event.source_ip:
                unique_sources.add(event.source_ip)
            if hasattr(event, 'destination_ip') and event.destination_ip:
                unique_destinations.add(event.destination_ip)
        
        features.update({
            'unique_source_ips': float(len(unique_sources)),
            'unique_destinations': float(len(unique_destinations)),
            'access_diversity_score': len(unique_sources) / max(total_events, 1)
        })
        
        return features
    
    async def _extract_volume_features(self, events: List[BaseEvent]) -> Dict[str, float]:
        """Extract volume-based features"""
        if not events:
            return {}
        
        total_events = len(events)
        time_span = (max(e.timestamp for e in events) - min(e.timestamp for e in events)).total_seconds() / 3600
        
        features = {
            'total_events': float(total_events),
            'events_per_hour': float(total_events / max(time_span, 1)),
        }
        
        # Data volume features for applicable events
        data_volumes = []
        for event in events:
            if hasattr(event, 'bytes_accessed') and event.bytes_accessed:
                data_volumes.append(event.bytes_accessed)
            elif hasattr(event, 'bytes_sent') and event.bytes_sent:
                data_volumes.append(event.bytes_sent)
            elif hasattr(event, 'bytes_received') and event.bytes_received:
                data_volumes.append(event.bytes_received)
        
        if data_volumes:
            features.update({
                'total_data_volume': float(sum(data_volumes)),
                'avg_data_volume': float(np.mean(data_volumes)),
                'max_data_volume': float(max(data_volumes)),
                'std_data_volume': float(np.std(data_volumes))
            })
        
        return features
    
    async def _extract_pattern_features(self, events: List[BaseEvent]) -> Dict[str, float]:
        """Extract behavioral pattern features"""
        if len(events) < 2:
            return {}
        
        # Session pattern analysis
        sessions = self._group_events_by_session(events)
        
        features = {
            'unique_sessions': float(len(sessions)),
            'avg_session_duration': 0.0,
            'avg_events_per_session': 0.0
        }
        
        if sessions:
            session_durations = []
            session_event_counts = []
            
            for session_events in sessions.values():
                if len(session_events) > 1:
                    duration = (max(e.timestamp for e in session_events) - 
                              min(e.timestamp for e in session_events)).total_seconds() / 60  # minutes
                    session_durations.append(duration)
                session_event_counts.append(len(session_events))
            
            if session_durations:
                features['avg_session_duration'] = float(np.mean(session_durations))
            features['avg_events_per_session'] = float(np.mean(session_event_counts))
        
        return features
    
    async def _extract_geographic_features(self, events: List[BaseEvent]) -> Dict[str, float]:
        """Extract geographic pattern features"""
        locations = []
        
        for event in events:
            if hasattr(event, 'source_location') and event.source_location:
                locations.append(event.source_location)
        
        if not locations:
            return {'unique_locations': 0.0, 'geographic_diversity': 0.0}
        
        unique_locations = len(set(str(loc) for loc in locations))
        
        # Calculate geographic spread
        if len(locations) > 1:
            distances = await self.geo_analyzer.calculate_location_distances(locations)
            max_distance = max(distances) if distances else 0
            avg_distance = np.mean(distances) if distances else 0
        else:
            max_distance = avg_distance = 0
        
        return {
            'unique_locations': float(unique_locations),
            'geographic_diversity': unique_locations / len(events),
            'max_geographic_distance': float(max_distance),
            'avg_geographic_distance': float(avg_distance)
        }
    
    async def _extract_auth_features(self, auth_events: List[AuthenticationEvent]) -> Dict[str, float]:
        """Extract authentication-specific features"""
        if not auth_events:
            return {}
        
        total_auth = len(auth_events)
        successful_auth = sum(1 for e in auth_events if e.result == 'success')
        failed_auth = sum(1 for e in auth_events if e.result == 'failure')
        mfa_used = sum(1 for e in auth_events if e.mfa_used)
        
        unique_methods = len(set(e.authentication_method for e in auth_events))
        
        return {
            'auth_success_rate': successful_auth / total_auth,
            'auth_failure_rate': failed_auth / total_auth,
            'mfa_usage_rate': mfa_used / total_auth,
            'auth_method_diversity': float(unique_methods),
            'total_auth_attempts': float(total_auth)
        }
    
    async def _analyze_temporal_patterns(self, events: List[BaseEvent]) -> Dict[str, Any]:
        """Analyze temporal behavior patterns"""
        if not events:
            return {}
        
        # Group events by time periods
        hourly_distribution = [0] * 24
        daily_distribution = [0] * 7
        
        for event in events:
            hourly_distribution[event.timestamp.hour] += 1
            daily_distribution[event.timestamp.weekday()] += 1
        
        # Find peak activity periods
        peak_hour = hourly_distribution.index(max(hourly_distribution))
        peak_day = daily_distribution.index(max(daily_distribution))
        
        # Calculate activity consistency
        hour_variance = np.var(hourly_distribution)
        day_variance = np.var(daily_distribution)
        
        return {
            'hourly_distribution': hourly_distribution,
            'daily_distribution': daily_distribution,
            'peak_activity_hour': peak_hour,
            'peak_activity_day': peak_day,
            'hourly_consistency': float(1.0 / (1.0 + hour_variance)),
            'daily_consistency': float(1.0 / (1.0 + day_variance)),
            'login_patterns': await self._analyze_login_patterns(events)
        }
    
    async def _analyze_login_patterns(self, events: List[BaseEvent]) -> Dict[str, Any]:
        """Analyze login-specific patterns"""
        auth_events = [e for e in events if isinstance(e, AuthenticationEvent)]
        
        if not auth_events:
            return {}
        
        # Login frequency analysis
        login_times = [e.timestamp for e in auth_events if e.result == 'success']
        
        if len(login_times) < 2:
            return {'login_frequency': 0, 'regular_login_pattern': False}
        
        # Calculate intervals between logins
        intervals = []
        for i in range(1, len(login_times)):
            interval = (login_times[i] - login_times[i-1]).total_seconds() / 3600  # hours
            intervals.append(interval)
        
        return {
            'login_frequency': len(login_times),
            'avg_login_interval': float(np.mean(intervals)),
            'login_interval_std': float(np.std(intervals)),
            'regular_login_pattern': np.std(intervals) < 12,  # Regular if std < 12 hours
            'login_success_rate': len(login_times) / len(auth_events)
        }
    
    async def _analyze_access_patterns(self, events: List[BaseEvent]) -> Dict[str, Any]:
        """Analyze access behavior patterns"""
        access_events = [e for e in events if isinstance(e, DataAccessEvent)]
        
        if not access_events:
            return {}
        
        # Resource access analysis
        resources_accessed = [e.resource_id for e in access_events]
        unique_resources = set(resources_accessed)
        
        # Access method analysis
        access_methods = [e.access_method for e in access_events if e.access_method]
        
        # Data classification analysis
        data_classifications = [e.data_classification for e in access_events if e.data_classification]
        
        return {
            'total_access_events': len(access_events),
            'unique_resources_accessed': len(unique_resources),
            'resource_diversity': len(unique_resources) / len(access_events),
            'most_accessed_resource': max(set(resources_accessed), key=resources_accessed.count) if resources_accessed else None,
            'access_methods': list(set(access_methods)),
            'sensitive_data_access': sum(1 for dc in data_classifications if dc in ['confidential', 'secret', 'top_secret'])
        }
    
    async def _analyze_geographic_patterns(self, events: List[BaseEvent]) -> Dict[str, Any]:
        """Analyze geographic behavior patterns"""
        locations = []
        
        for event in events:
            if hasattr(event, 'source_location') and event.source_location:
                locations.append(event.source_location)
        
        if not locations:
            return {}
        
        # Location diversity
        unique_locations = set(str(loc) for loc in locations)
        
        # Calculate impossible travel scenarios
        impossible_travel_events = await self.geo_analyzer.detect_impossible_travel(events)
        
        return {
            'unique_locations': len(unique_locations),
            'location_diversity': len(unique_locations) / len(events),
            'impossible_travel_detected': len(impossible_travel_events) > 0,
            'impossible_travel_count': len(impossible_travel_events),
            'primary_locations': await self._identify_primary_locations(locations)
        }
    
    async def _detect_anomalies(
        self,
        entity: Entity,
        features: FeatureVector,
        events: List[BaseEvent]
    ) -> List[AnomalyDetection]:
        """Detect anomalies in entity behavior"""
        anomalies = []
        
        try:
            # Get baseline for entity
            baseline = await self._get_or_create_baseline(entity)
            
            if not baseline:
                logger.warning(f"No baseline available for entity {entity.entity_id}")
                return anomalies
            
            # Time-based anomaly detection
            time_anomalies = await self._detect_time_anomalies(entity, features, baseline)
            anomalies.extend(time_anomalies)
            
            # Volume-based anomaly detection
            volume_anomalies = await self._detect_volume_anomalies(entity, features, baseline)
            anomalies.extend(volume_anomalies)
            
            # Pattern-based anomaly detection
            pattern_anomalies = await self._detect_pattern_anomalies(entity, features, baseline)
            anomalies.extend(pattern_anomalies)
            
            # Geographic anomaly detection
            geo_anomalies = await self._detect_geographic_anomalies(entity, events)
            anomalies.extend(geo_anomalies)
            
            logger.info(f"Detected {len(anomalies)} anomalies for entity {entity.entity_id}")
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
        
        return anomalies
    
    async def _detect_time_anomalies(
        self,
        entity: Entity,
        features: FeatureVector,
        baseline: BehaviorBaseline
    ) -> List[AnomalyDetection]:
        """Detect time-based anomalies"""
        anomalies = []
        
        try:
            # Check if current activity time is unusual
            current_hour = datetime.utcnow().hour
            baseline_hours = baseline.features.get('typical_hours', [])
            
            if baseline_hours and current_hour not in baseline_hours:
                # Calculate deviation score
                hour_frequencies = baseline.statistical_measures.get('hourly_frequency', {})
                current_frequency = hour_frequencies.get(str(current_hour), 0)
                max_frequency = max(hour_frequencies.values()) if hour_frequencies else 1
                
                anomaly_score = 1.0 - (current_frequency / max_frequency)
                
                if anomaly_score > AnalyticsConfig.BASELINE_THRESHOLDS['login_frequency_std_multiplier'] * 0.1:
                    anomaly = AnomalyDetection(
                        entity_id=entity.entity_id,
                        anomaly_type=AnomalyType.TIME_ANOMALY,
                        anomaly_score=anomaly_score,
                        confidence=0.8,
                        threshold=0.3,
                        baseline_id=baseline.id,
                        features_analyzed={'current_hour': current_hour, 'typical_hours': baseline_hours},
                        deviation_details={'hour_deviation': anomaly_score}
                    )
                    anomalies.append(anomaly)
            
        except Exception as e:
            logger.error(f"Error detecting time anomalies: {e}")
        
        return anomalies
    
    async def _detect_volume_anomalies(
        self,
        entity: Entity,
        features: FeatureVector,
        baseline: BehaviorBaseline
    ) -> List[AnomalyDetection]:
        """Detect volume-based anomalies"""
        anomalies = []
        
        try:
            current_volume = features.features.get('total_events', 0)
            baseline_volume = baseline.statistical_measures.get('avg_events_per_hour', 0)
            baseline_std = baseline.statistical_measures.get('events_std', 1)
            
            if baseline_volume > 0:
                z_score = abs(current_volume - baseline_volume) / baseline_std
                
                if z_score > AnalyticsConfig.BASELINE_THRESHOLDS['login_frequency_std_multiplier']:
                    anomaly_score = min(z_score / 10.0, 1.0)  # Normalize to 0-1
                    
                    anomaly = AnomalyDetection(
                        entity_id=entity.entity_id,
                        anomaly_type=AnomalyType.VOLUME_ANOMALY,
                        anomaly_score=anomaly_score,
                        confidence=0.7,
                        threshold=0.4,
                        baseline_id=baseline.id,
                        features_analyzed={'current_volume': current_volume, 'baseline_volume': baseline_volume},
                        deviation_details={'z_score': z_score, 'std_deviations': z_score}
                    )
                    anomalies.append(anomaly)
            
        except Exception as e:
            logger.error(f"Error detecting volume anomalies: {e}")
        
        return anomalies
    
    async def _detect_pattern_anomalies(
        self,
        entity: Entity,
        features: FeatureVector,
        baseline: BehaviorBaseline
    ) -> List[AnomalyDetection]:
        """Detect pattern-based anomalies using ML models"""
        anomalies = []
        
        try:
            # Prepare feature vector for ML models
            feature_vector = self._prepare_feature_vector(features, baseline)
            
            if len(feature_vector) == 0:
                return anomalies
            
            # Use ensemble approach with multiple models
            isolation_score = self._detect_with_isolation_forest(feature_vector)
            
            if isolation_score < -0.5:  # Anomaly threshold
                anomaly_score = abs(isolation_score)
                
                anomaly = AnomalyDetection(
                    entity_id=entity.entity_id,
                    anomaly_type=AnomalyType.PATTERN_ANOMALY,
                    anomaly_score=anomaly_score,
                    confidence=0.75,
                    threshold=0.5,
                    baseline_id=baseline.id,
                    features_analyzed=features.features,
                    deviation_details={'isolation_score': isolation_score}
                )
                anomalies.append(anomaly)
            
        except Exception as e:
            logger.error(f"Error detecting pattern anomalies: {e}")
        
        return anomalies
    
    async def _detect_geographic_anomalies(
        self,
        entity: Entity,
        events: List[BaseEvent]
    ) -> List[AnomalyDetection]:
        """Detect geographic anomalies"""
        anomalies = []
        
        try:
            # Detect impossible travel
            impossible_travel_events = await self.geo_analyzer.detect_impossible_travel(events)
            
            for event_pair in impossible_travel_events:
                anomaly = AnomalyDetection(
                    entity_id=entity.entity_id,
                    event_id=event_pair['later_event'].event_id,
                    anomaly_type=AnomalyType.LOCATION_ANOMALY,
                    anomaly_score=0.9,  # High score for impossible travel
                    confidence=0.95,
                    threshold=0.7,
                    features_analyzed={
                        'distance_km': event_pair['distance'],
                        'time_difference_hours': event_pair['time_diff'],
                        'required_speed_kmh': event_pair['required_speed']
                    },
                    deviation_details={'impossible_travel': True}
                )
                anomalies.append(anomaly)
            
        except Exception as e:
            logger.error(f"Error detecting geographic anomalies: {e}")
        
        return anomalies
    
    def _prepare_feature_vector(self, features: FeatureVector, baseline: BehaviorBaseline) -> np.ndarray:
        """Prepare feature vector for ML models"""
        try:
            # Select numerical features
            feature_names = [
                'avg_hour_of_day', 'std_hour_of_day', 'weekend_activity_ratio',
                'night_activity_ratio', 'business_hours_ratio', 'total_events',
                'events_per_hour', 'unique_source_ips', 'access_diversity_score'
            ]
            
            vector = []
            for name in feature_names:
                value = features.features.get(name, 0.0)
                vector.append(float(value))
            
            return np.array(vector).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Error preparing feature vector: {e}")
            return np.array([])
    
    def _detect_with_isolation_forest(self, feature_vector: np.ndarray) -> float:
        """Detect anomalies using Isolation Forest"""
        try:
            if 'isolation_forest' not in self.models:
                return 0.0
            
            # Normalize features
            if feature_vector.shape[1] > 0:
                normalized = self.scalers['standard'].fit_transform(feature_vector)
                score = self.models['isolation_forest'].decision_function(normalized)[0]
                return float(score)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error in isolation forest detection: {e}")
            return 0.0
    
    async def _get_or_create_baseline(self, entity: Entity) -> Optional[BehaviorBaseline]:
        """Get existing baseline or create new one for entity"""
        try:
            # Check if baseline exists
            if entity.entity_id in self.baselines:
                return self.baselines[entity.entity_id]
            
            # Create new baseline if entity has enough historical data
            if entity.baseline_established:
                baseline = await self._create_baseline(entity)
                if baseline:
                    self.baselines[entity.entity_id] = baseline
                return baseline
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting/creating baseline: {e}")
            return None
    
    async def _create_baseline(self, entity: Entity) -> Optional[BehaviorBaseline]:
        """Create behavioral baseline for entity"""
        try:
            # This would typically fetch historical data from database
            # For now, return a mock baseline
            baseline = BehaviorBaseline(
                entity_id=entity.entity_id,
                entity_type=entity.entity_type,
                baseline_period_start=datetime.utcnow() - timedelta(days=30),
                baseline_period_end=datetime.utcnow(),
                features={
                    'typical_hours': list(range(9, 18)),  # Business hours
                    'typical_days': list(range(0, 5)),    # Weekdays
                    'common_locations': ['office', 'home']
                },
                statistical_measures={
                    'avg_events_per_hour': 15.0,
                    'events_std': 5.0,
                    'hourly_frequency': {str(h): 0.1 for h in range(24)}
                },
                confidence_score=0.8
            )
            
            return baseline
            
        except Exception as e:
            logger.error(f"Error creating baseline: {e}")
            return None
    
    async def _identify_risk_indicators(
        self,
        entity: Entity,
        events: List[BaseEvent],
        anomalies: List[AnomalyDetection]
    ) -> List[str]:
        """Identify risk indicators for the entity"""
        risk_indicators = []
        
        try:
            # High anomaly count
            if len(anomalies) > 5:
                risk_indicators.append("high_anomaly_count")
            
            # Failed authentication attempts
            auth_events = [e for e in events if isinstance(e, AuthenticationEvent)]
            failed_auths = [e for e in auth_events if e.result == 'failure']
            if len(failed_auths) > 3:
                risk_indicators.append("multiple_failed_authentications")
            
            # Off-hours activity
            off_hours_events = [e for e in events if e.timestamp.hour < 6 or e.timestamp.hour > 22]
            if len(off_hours_events) > len(events) * 0.3:
                risk_indicators.append("unusual_time_activity")
            
            # Access to sensitive resources
            data_events = [e for e in events if isinstance(e, DataAccessEvent)]
            sensitive_access = [e for e in data_events if e.data_classification in ['confidential', 'secret']]
            if len(sensitive_access) > 0:
                risk_indicators.append("sensitive_data_access")
            
            # Geographic anomalies
            geo_anomalies = [a for a in anomalies if a.anomaly_type == AnomalyType.LOCATION_ANOMALY]
            if geo_anomalies:
                risk_indicators.append("geographic_anomaly")
            
        except Exception as e:
            logger.error(f"Error identifying risk indicators: {e}")
        
        return risk_indicators
    
    async def _detect_behavioral_changes(
        self,
        entity: Entity,
        features: FeatureVector
    ) -> List[Dict[str, Any]]:
        """Detect significant behavioral changes"""
        changes = []
        
        try:
            # Get historical profile
            if entity.entity_id in self.entity_profiles:
                previous_profile = self.entity_profiles[entity.entity_id]
                
                # Compare key behavioral metrics
                current_features = features.features
                previous_features = previous_profile.get('features', {})
                
                # Check for significant changes in activity patterns
                for feature_name in ['avg_hour_of_day', 'events_per_hour', 'access_diversity_score']:
                    current_value = current_features.get(feature_name, 0)
                    previous_value = previous_features.get(feature_name, 0)
                    
                    if previous_value > 0:
                        change_ratio = abs(current_value - previous_value) / previous_value
                        if change_ratio > 0.5:  # 50% change threshold
                            changes.append({
                                'feature': feature_name,
                                'previous_value': previous_value,
                                'current_value': current_value,
                                'change_ratio': change_ratio,
                                'change_type': 'increase' if current_value > previous_value else 'decrease'
                            })
            
        except Exception as e:
            logger.error(f"Error detecting behavioral changes: {e}")
        
        return changes
    
    def _create_activity_summary(self, events: List[BaseEvent]) -> Dict[str, Any]:
        """Create activity summary from events"""
        if not events:
            return {}
        
        event_types = [e.event_type for e in events]
        event_type_counts = {et.value: event_types.count(et) for et in EventType}
        
        return {
            'total_events': len(events),
            'event_types': event_type_counts,
            'time_range': {
                'start': min(e.timestamp for e in events).isoformat(),
                'end': max(e.timestamp for e in events).isoformat()
            },
            'unique_sessions': len(self._group_events_by_session(events))
        }
    
    def _group_events_by_session(self, events: List[BaseEvent]) -> Dict[str, List[BaseEvent]]:
        """Group events by session ID"""
        sessions = {}
        
        for event in events:
            session_id = getattr(event, 'session_id', 'unknown')
            if session_id not in sessions:
                sessions[session_id] = []
            sessions[session_id].append(event)
        
        return sessions
    
    async def _identify_primary_locations(self, locations: List[Dict[str, Any]]) -> List[str]:
        """Identify primary locations for the entity"""
        if not locations:
            return []
        
        # Count location frequencies
        location_counts = {}
        for loc in locations:
            loc_str = str(loc)
            location_counts[loc_str] = location_counts.get(loc_str, 0) + 1
        
        # Return top 3 most frequent locations
        sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
        return [loc for loc, count in sorted_locations[:3]]
    
    def _create_empty_analysis(
        self,
        entity: Entity,
        time_window_hours: int
    ) -> UserBehaviorAnalysis:
        """Create empty analysis result"""
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        return UserBehaviorAnalysis(
            user_id=entity.entity_id,
            analysis_period_start=cutoff_time,
            analysis_period_end=datetime.utcnow(),
            activity_summary={},
            login_patterns={},
            access_patterns={},
            geographic_patterns={},
            temporal_patterns={},
            anomalies_detected=[],
            risk_indicators=[],
            behavioral_changes=[]
        ) 