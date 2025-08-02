"""
UEBA Risk Scoring System
Calculates and updates risk scores for entities based on behavioral analysis
"""
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from loguru import logger

from ..models.schemas import (
    Entity, BaseEvent, RiskScore, RiskLevel, AnomalyDetection,
    AnomalyType, AlertSeverity, EntityType
)
from ..config.settings import settings, AnalyticsConfig


class RiskScorer:
    """Calculates risk scores for entities based on behavior and anomalies"""
    
    def __init__(self):
        self.risk_factors = AnalyticsConfig.RISK_FACTORS
        self.risk_cache = {}
        self.historical_scores = {}
        
        logger.info("Risk Scorer initialized")
    
    async def calculate_entity_risk(
        self,
        entity: Entity,
        events: List[BaseEvent],
        anomalies: List[AnomalyDetection],
        time_window_hours: int = 24
    ) -> RiskScore:
        """
        Calculate comprehensive risk score for an entity
        
        Args:
            entity: Entity to score
            events: Recent events for the entity
            anomalies: Detected anomalies
            time_window_hours: Time window for analysis
            
        Returns:
            Risk score with breakdown
        """
        try:
            logger.info(f"Calculating risk score for entity {entity.entity_id}")
            
            # Initialize risk factors
            risk_factors = {}
            
            # Calculate anomaly-based risk
            risk_factors.update(await self._calculate_anomaly_risk(anomalies))
            
            # Calculate temporal risk
            risk_factors.update(await self._calculate_temporal_risk(events))
            
            # Calculate volume risk
            risk_factors.update(await self._calculate_volume_risk(events, entity))
            
            # Calculate access pattern risk
            risk_factors.update(await self._calculate_access_risk(events))
            
            # Calculate behavioral change risk
            risk_factors.update(await self._calculate_behavioral_change_risk(entity, events))
            
            # Calculate entity-specific risk
            risk_factors.update(await self._calculate_entity_specific_risk(entity))
            
            # Calculate overall score using weighted combination
            overall_score = await self._calculate_weighted_score(risk_factors)
            
            # Apply decay if applicable
            overall_score = await self._apply_time_decay(entity, overall_score)
            
            # Determine risk level
            risk_level = self._determine_risk_level(overall_score)
            
            # Get contributing events
            contributing_events = [e.event_id for e in events[-10:]]  # Last 10 events
            
            risk_score = RiskScore(
                entity_id=entity.entity_id,
                entity_type=entity.entity_type,
                overall_score=overall_score,
                risk_level=risk_level,
                risk_factors=risk_factors,
                contributing_events=contributing_events,
                calculation_method="weighted_ensemble",
                decay_applied=True
            )
            
            # Cache the score
            self.risk_cache[entity.entity_id] = risk_score
            
            # Update historical scores
            await self._update_historical_scores(entity.entity_id, overall_score)
            
            logger.info(f"Risk score calculated for {entity.entity_id}: {overall_score:.3f} ({risk_level})")
            return risk_score
            
        except Exception as e:
            logger.error(f"Error calculating risk score for {entity.entity_id}: {e}")
            return self._create_default_risk_score(entity)
    
    async def update_risk_score(
        self,
        entity_id: str,
        additional_risk: float,
        reason: str
    ):
        """Update risk score with additional risk factor"""
        try:
            if entity_id in self.risk_cache:
                current_score = self.risk_cache[entity_id]
                
                # Add additional risk
                new_score = min(current_score.overall_score + additional_risk, 1.0)
                current_score.overall_score = new_score
                current_score.risk_level = self._determine_risk_level(new_score)
                current_score.risk_factors[f'manual_adjustment_{datetime.utcnow().timestamp()}'] = additional_risk
                
                logger.info(f"Updated risk score for {entity_id}: {new_score:.3f} (reason: {reason})")
            
        except Exception as e:
            logger.error(f"Error updating risk score: {e}")
    
    async def get_risk_trend(
        self,
        entity_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get risk score trend for entity"""
        try:
            if entity_id not in self.historical_scores:
                return {}
            
            scores = self.historical_scores[entity_id]
            
            # Filter by time range
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            recent_scores = [
                (timestamp, score) for timestamp, score in scores
                if timestamp >= cutoff_time
            ]
            
            if len(recent_scores) < 2:
                return {}
            
            # Calculate trend metrics
            score_values = [score for _, score in recent_scores]
            
            trend = {
                'current_score': score_values[-1],
                'min_score': min(score_values),
                'max_score': max(score_values),
                'avg_score': sum(score_values) / len(score_values),
                'trend_direction': 'increasing' if score_values[-1] > score_values[0] else 'decreasing',
                'volatility': self._calculate_volatility(score_values),
                'data_points': len(recent_scores)
            }
            
            return trend
            
        except Exception as e:
            logger.error(f"Error getting risk trend: {e}")
            return {}
    
    async def get_high_risk_entities(
        self,
        threshold: float = 0.7,
        limit: int = 100
    ) -> List[RiskScore]:
        """Get entities with high risk scores"""
        try:
            high_risk_entities = []
            
            for entity_id, risk_score in self.risk_cache.items():
                if risk_score.overall_score >= threshold:
                    high_risk_entities.append(risk_score)
            
            # Sort by risk score (highest first)
            high_risk_entities.sort(key=lambda x: x.overall_score, reverse=True)
            
            return high_risk_entities[:limit]
            
        except Exception as e:
            logger.error(f"Error getting high risk entities: {e}")
            return []
    
    async def _calculate_anomaly_risk(self, anomalies: List[AnomalyDetection]) -> Dict[str, float]:
        """Calculate risk based on detected anomalies"""
        risk_factors = {}
        
        if not anomalies:
            return {
                'anomaly_count_risk': 0.0,
                'anomaly_severity_risk': 0.0
            }
        
        # Count anomalies by type
        anomaly_counts = {}
        total_anomaly_score = 0.0
        
        for anomaly in anomalies:
            anomaly_type = anomaly.anomaly_type
            anomaly_counts[anomaly_type] = anomaly_counts.get(anomaly_type, 0) + 1
            total_anomaly_score += anomaly.anomaly_score
        
        # Calculate risk based on anomaly count
        anomaly_count_risk = min(len(anomalies) / 10.0, 1.0)  # Normalize to 0-1
        
        # Calculate risk based on average anomaly severity
        avg_anomaly_score = total_anomaly_score / len(anomalies)
        anomaly_severity_risk = avg_anomaly_score
        
        # Add specific anomaly type risks
        risk_factors['anomaly_count_risk'] = anomaly_count_risk
        risk_factors['anomaly_severity_risk'] = anomaly_severity_risk
        
        # High-risk anomaly types
        if AnomalyType.LOCATION_ANOMALY in anomaly_counts:
            risk_factors['location_anomaly_risk'] = min(anomaly_counts[AnomalyType.LOCATION_ANOMALY] / 3.0, 1.0)
        
        if AnomalyType.TIME_ANOMALY in anomaly_counts:
            risk_factors['time_anomaly_risk'] = min(anomaly_counts[AnomalyType.TIME_ANOMALY] / 5.0, 1.0)
        
        if AnomalyType.ACCESS_ANOMALY in anomaly_counts:
            risk_factors['access_anomaly_risk'] = min(anomaly_counts[AnomalyType.ACCESS_ANOMALY] / 3.0, 1.0)
        
        return risk_factors
    
    async def _calculate_temporal_risk(self, events: List[BaseEvent]) -> Dict[str, float]:
        """Calculate risk based on temporal patterns"""
        risk_factors = {}
        
        if not events:
            return {'temporal_risk': 0.0}
        
        current_time = datetime.utcnow()
        
        # Off-hours activity risk
        off_hours_events = 0
        weekend_events = 0
        night_events = 0
        
        for event in events:
            hour = event.timestamp.hour
            weekday = event.timestamp.weekday()
            
            # Off business hours (before 8 AM or after 6 PM)
            if hour < 8 or hour > 18:
                off_hours_events += 1
            
            # Weekend activity (Saturday=5, Sunday=6)
            if weekday >= 5:
                weekend_events += 1
            
            # Night activity (10 PM to 6 AM)
            if hour >= 22 or hour <= 6:
                night_events += 1
        
        total_events = len(events)
        
        risk_factors['off_hours_risk'] = off_hours_events / total_events
        risk_factors['weekend_risk'] = weekend_events / total_events
        risk_factors['night_activity_risk'] = night_events / total_events
        
        # Activity burst risk (many events in short time)
        if total_events > 10:
            time_span = (max(e.timestamp for e in events) - min(e.timestamp for e in events)).total_seconds() / 3600
            if time_span > 0:
                event_rate = total_events / time_span
                # High event rate indicates potential automation or malicious activity
                risk_factors['activity_burst_risk'] = min(event_rate / 100.0, 1.0)
            else:
                risk_factors['activity_burst_risk'] = 1.0  # All events at same time
        else:
            risk_factors['activity_burst_risk'] = 0.0
        
        return risk_factors
    
    async def _calculate_volume_risk(self, events: List[BaseEvent], entity: Entity) -> Dict[str, float]:
        """Calculate risk based on activity volume"""
        risk_factors = {}
        
        if not events:
            return {'volume_risk': 0.0}
        
        # Calculate event volume metrics
        total_events = len(events)
        
        # Get time span
        if total_events > 1:
            time_span_hours = (max(e.timestamp for e in events) - min(e.timestamp for e in events)).total_seconds() / 3600
            events_per_hour = total_events / max(time_span_hours, 1)
        else:
            events_per_hour = total_events
        
        # Compare to baseline (if available)
        # For now, use simple thresholds
        normal_events_per_hour = 10.0  # This would come from entity baseline
        
        if events_per_hour > normal_events_per_hour * 3:
            risk_factors['high_volume_risk'] = min((events_per_hour / normal_events_per_hour) / 10.0, 1.0)
        else:
            risk_factors['high_volume_risk'] = 0.0
        
        # Data volume risk (if applicable)
        total_data_bytes = 0
        for event in events:
            if hasattr(event, 'bytes_accessed') and event.bytes_accessed:
                total_data_bytes += event.bytes_accessed
            elif hasattr(event, 'bytes_sent') and event.bytes_sent:
                total_data_bytes += event.bytes_sent
        
        if total_data_bytes > 0:
            # Convert to MB
            data_mb = total_data_bytes / (1024 * 1024)
            # Risk increases with data volume
            risk_factors['data_volume_risk'] = min(data_mb / 1000.0, 1.0)  # Risk at 1GB
        else:
            risk_factors['data_volume_risk'] = 0.0
        
        return risk_factors
    
    async def _calculate_access_risk(self, events: List[BaseEvent]) -> Dict[str, float]:
        """Calculate risk based on access patterns"""
        risk_factors = {}
        
        if not events:
            return {'access_risk': 0.0}
        
        # Failed access attempts
        failed_attempts = 0
        successful_attempts = 0
        
        # Sensitive resource access
        sensitive_access = 0
        
        # Multiple IP addresses
        unique_ips = set()
        
        for event in events:
            # Count authentication results
            if hasattr(event, 'result'):
                if event.result == 'failure':
                    failed_attempts += 1
                elif event.result == 'success':
                    successful_attempts += 1
            
            # Check for sensitive data access
            if hasattr(event, 'data_classification'):
                if event.data_classification in ['confidential', 'secret', 'top_secret']:
                    sensitive_access += 1
            
            # Track IP addresses
            if hasattr(event, 'source_ip') and event.source_ip:
                unique_ips.add(event.source_ip)
        
        total_attempts = failed_attempts + successful_attempts
        
        # Calculate risk factors
        if total_attempts > 0:
            risk_factors['failed_access_risk'] = failed_attempts / total_attempts
        else:
            risk_factors['failed_access_risk'] = 0.0
        
        risk_factors['sensitive_access_risk'] = min(sensitive_access / 5.0, 1.0)  # Risk at 5+ sensitive accesses
        risk_factors['multiple_ip_risk'] = min(len(unique_ips) / 10.0, 1.0)  # Risk at 10+ IPs
        
        # Brute force risk (many failed attempts)
        if failed_attempts >= 10:
            risk_factors['brute_force_risk'] = min(failed_attempts / 50.0, 1.0)
        else:
            risk_factors['brute_force_risk'] = 0.0
        
        return risk_factors
    
    async def _calculate_behavioral_change_risk(self, entity: Entity, events: List[BaseEvent]) -> Dict[str, float]:
        """Calculate risk based on behavioral changes"""
        risk_factors = {}
        
        # This would compare current behavior to established baseline
        # For now, return simple metrics
        
        # Check for dormant account sudden activity
        if entity.last_activity:
            days_since_last = (datetime.utcnow() - entity.last_activity).days
            if days_since_last > 30 and events:  # Dormant for 30+ days but now active
                risk_factors['dormant_reactivation_risk'] = min(days_since_last / 365.0, 1.0)
            else:
                risk_factors['dormant_reactivation_risk'] = 0.0
        else:
            risk_factors['dormant_reactivation_risk'] = 0.0
        
        # Pattern deviation risk (would be calculated against baseline)
        risk_factors['pattern_deviation_risk'] = 0.0  # Placeholder
        
        return risk_factors
    
    async def _calculate_entity_specific_risk(self, entity: Entity) -> Dict[str, float]:
        """Calculate risk factors specific to entity type and attributes"""
        risk_factors = {}
        
        # Privileged entity risk
        if hasattr(entity, 'is_privileged') and entity.is_privileged:
            risk_factors['privileged_entity_risk'] = 0.3  # Higher baseline for privileged entities
        else:
            risk_factors['privileged_entity_risk'] = 0.0
        
        # External entity risk
        if hasattr(entity, 'is_external') and getattr(entity, 'is_external', False):
            risk_factors['external_entity_risk'] = 0.2
        else:
            risk_factors['external_entity_risk'] = 0.0
        
        # Service account risk
        if entity.entity_type == EntityType.SERVICE_ACCOUNT:
            risk_factors['service_account_risk'] = 0.1  # Slight increase for service accounts
        else:
            risk_factors['service_account_risk'] = 0.0
        
        # Device trust risk
        if entity.entity_type == EntityType.DEVICE:
            if hasattr(entity, 'is_trusted') and not entity.is_trusted:
                risk_factors['untrusted_device_risk'] = 0.4
            else:
                risk_factors['untrusted_device_risk'] = 0.0
        
        return risk_factors
    
    async def _calculate_weighted_score(self, risk_factors: Dict[str, float]) -> float:
        """Calculate weighted overall risk score"""
        if not risk_factors:
            return 0.0
        
        # Define weights for different risk categories
        weights = {
            # Anomaly-based risks (high weight)
            'anomaly_count_risk': 0.15,
            'anomaly_severity_risk': 0.15,
            'location_anomaly_risk': 0.10,
            'access_anomaly_risk': 0.10,
            
            # Temporal risks (medium weight)
            'off_hours_risk': 0.05,
            'weekend_risk': 0.03,
            'night_activity_risk': 0.05,
            'activity_burst_risk': 0.08,
            
            # Access risks (high weight)
            'failed_access_risk': 0.10,
            'sensitive_access_risk': 0.08,
            'brute_force_risk': 0.12,
            
            # Volume risks (medium weight)
            'high_volume_risk': 0.06,
            'data_volume_risk': 0.04,
            
            # Entity-specific risks (medium weight)
            'privileged_entity_risk': 0.05,
            'external_entity_risk': 0.04,
            'untrusted_device_risk': 0.08,
            
            # Behavioral change risks (medium weight)
            'dormant_reactivation_risk': 0.06,
            'pattern_deviation_risk': 0.07
        }
        
        # Calculate weighted sum
        weighted_score = 0.0
        total_weight = 0.0
        
        for factor_name, factor_value in risk_factors.items():
            weight = weights.get(factor_name, 0.01)  # Default small weight for unknown factors
            weighted_score += factor_value * weight
            total_weight += weight
        
        # Normalize if needed
        if total_weight > 0:
            normalized_score = weighted_score / total_weight
        else:
            normalized_score = 0.0
        
        # Ensure score is between 0 and 1
        return max(0.0, min(normalized_score, 1.0))
    
    async def _apply_time_decay(self, entity: Entity, score: float) -> float:
        """Apply time-based decay to risk score"""
        # Risk scores should decay over time if no new risk factors are observed
        if entity.entity_id in self.historical_scores:
            scores = self.historical_scores[entity.entity_id]
            if scores:
                last_timestamp, last_score = scores[-1]
                hours_since_last = (datetime.utcnow() - last_timestamp).total_seconds() / 3600
                
                # Apply exponential decay (half-life of 24 hours)
                decay_factor = math.exp(-0.693 * hours_since_last / 24)
                decayed_score = score * decay_factor
                
                return max(decayed_score, 0.0)
        
        return score
    
    def _determine_risk_level(self, score: float) -> RiskLevel:
        """Determine risk level from numeric score"""
        if score >= 0.8:
            return RiskLevel.VERY_HIGH
        elif score >= 0.6:
            return RiskLevel.HIGH
        elif score >= 0.4:
            return RiskLevel.MEDIUM
        elif score >= 0.2:
            return RiskLevel.LOW
        else:
            return RiskLevel.VERY_LOW
    
    async def _update_historical_scores(self, entity_id: str, score: float):
        """Update historical risk scores"""
        if entity_id not in self.historical_scores:
            self.historical_scores[entity_id] = []
        
        self.historical_scores[entity_id].append((datetime.utcnow(), score))
        
        # Keep only last 30 days of scores
        cutoff_time = datetime.utcnow() - timedelta(days=30)
        self.historical_scores[entity_id] = [
            (timestamp, score) for timestamp, score in self.historical_scores[entity_id]
            if timestamp >= cutoff_time
        ]
    
    def _calculate_volatility(self, scores: List[float]) -> float:
        """Calculate volatility of risk scores"""
        if len(scores) < 2:
            return 0.0
        
        # Calculate standard deviation
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        volatility = math.sqrt(variance)
        
        return volatility
    
    def _create_default_risk_score(self, entity: Entity) -> RiskScore:
        """Create default risk score for entity"""
        return RiskScore(
            entity_id=entity.entity_id,
            entity_type=entity.entity_type,
            overall_score=0.0,
            risk_level=RiskLevel.VERY_LOW,
            risk_factors={},
            contributing_events=[],
            calculation_method="default"
        ) 