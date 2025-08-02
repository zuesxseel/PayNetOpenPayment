"""
UEBA (User Entity Behavior Analytics) Main System
Central orchestration and API for behavioral analytics
"""
import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Callable
from uuid import uuid4
from loguru import logger

from .models.schemas import (
    Entity, User, Device, Application, BaseEvent, AuthenticationEvent,
    DataAccessEvent, NetworkAccessEvent, AnalysisRequest, AnalysisResponse,
    UserBehaviorAnalysis, Alert, AlertSeverity, AlertStatus, RiskScore,
    RiskLevel, SystemHealth, SecurityMetrics, EntityType, EventType
)
from .analytics.behavior_engine import BehaviorEngine
from .config.settings import settings
from .alerts.alert_manager import AlertManager
from .collectors.event_collector import EventCollector
from .detectors.risk_scorer import RiskScorer


class UEBASystem:
    """Main UEBA system orchestrator"""
    
    def __init__(self):
        self.behavior_engine = BehaviorEngine()
        self.alert_manager = AlertManager()
        self.event_collector = EventCollector()
        self.risk_scorer = RiskScorer()
        self.active_sessions = {}
        self.system_metrics = {}
        
        logger.info("UEBA System initialized")
    
    async def analyze_entity_behavior(
        self,
        request: AnalysisRequest,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> AnalysisResponse:
        """
        Analyze behavior for one or more entities
        
        Args:
            request: Analysis request containing entity IDs and parameters
            progress_callback: Optional callback for progress updates
            
        Returns:
            Comprehensive analysis response
        """
        start_time = time.time()
        request_id = uuid4()
        
        try:
            logger.info(f"Starting behavior analysis request {request_id}")
            
            if progress_callback:
                progress_callback("Initializing analysis", 0.0)
            
            # Collect entities
            entities = await self._collect_entities(request.entity_ids, request.entity_type)
            
            if not entities:
                return AnalysisResponse(
                    request_id=request_id,
                    status="error",
                    results={"error": "No entities found"},
                    processing_time=time.time() - start_time
                )
            
            if progress_callback:
                progress_callback("Entities collected", 20.0)
            
            # Collect events for the analysis period
            events_by_entity = await self._collect_events_for_entities(
                entities, request.start_time, request.end_time
            )
            
            if progress_callback:
                progress_callback("Events collected", 40.0)
            
            # Perform behavioral analysis
            analyses = []
            anomalies = []
            risk_scores = []
            alerts = []
            
            entity_count = len(entities)
            for i, entity in enumerate(entities):
                entity_events = events_by_entity.get(entity.entity_id, [])
                
                # Analyze behavior
                if "anomaly_detection" in request.analysis_types or "behavioral_analysis" in request.analysis_types:
                    analysis = await self.behavior_engine.analyze_entity_behavior(
                        entity, entity_events
                    )
                    analyses.append(analysis)
                    
                    # Extract anomalies from analysis
                    if analysis.anomalies_detected:
                        entity_anomalies = await self._get_anomalies_by_ids(analysis.anomalies_detected)
                        anomalies.extend(entity_anomalies)
                
                # Calculate risk scores
                if "risk_scoring" in request.analysis_types:
                    risk_score = await self.risk_scorer.calculate_entity_risk(
                        entity, entity_events, anomalies
                    )
                    risk_scores.append(risk_score)
                    
                    # Generate alerts if risk is high
                    if risk_score.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
                        alert = await self._create_risk_alert(entity, risk_score, anomalies)
                        alerts.append(alert)
                
                # Update progress
                if progress_callback:
                    progress = 40.0 + (50.0 * (i + 1) / entity_count)
                    progress_callback(f"Analyzed entity {i + 1}/{entity_count}", progress)
            
            # Process alerts
            for alert in alerts:
                await self.alert_manager.process_alert(alert)
            
            if progress_callback:
                progress_callback("Processing complete", 100.0)
            
            processing_time = time.time() - start_time
            
            # Create response
            response = AnalysisResponse(
                request_id=request_id,
                status="completed",
                results={
                    "entities_analyzed": len(entities),
                    "events_processed": sum(len(events) for events in events_by_entity.values()),
                    "anomalies_detected": len(anomalies),
                    "high_risk_entities": len([rs for rs in risk_scores if rs.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]]),
                    "alerts_generated": len(alerts)
                },
                anomalies=anomalies,
                risk_scores=risk_scores,
                alerts=alerts,
                processing_time=processing_time
            )
            
            logger.info(f"Analysis request {request_id} completed in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error in behavior analysis: {e}")
            return AnalysisResponse(
                request_id=request_id,
                status="error",
                results={"error": str(e)},
                processing_time=time.time() - start_time
            )
    
    async def monitor_real_time_events(
        self,
        event_stream: Any,
        callback: Callable[[List[Alert]], None]
    ):
        """
        Monitor real-time event stream for behavioral anomalies
        
        Args:
            event_stream: Stream of incoming events
            callback: Callback function for generated alerts
        """
        try:
            logger.info("Starting real-time event monitoring")
            
            async for event_batch in event_stream:
                alerts = []
                
                # Process each event
                for event in event_batch:
                    # Get entity for this event
                    entity = await self._get_entity_for_event(event)
                    if not entity:
                        continue
                    
                    # Quick anomaly check for real-time processing
                    anomalies = await self._quick_anomaly_detection(entity, event)
                    
                    # Generate alerts for significant anomalies
                    for anomaly in anomalies:
                        if anomaly.anomaly_score > settings.anomaly_detection_sensitivity:
                            alert = await self._create_anomaly_alert(entity, anomaly, event)
                            alerts.append(alert)
                            await self.alert_manager.process_alert(alert)
                
                # Callback with generated alerts
                if alerts and callback:
                    callback(alerts)
                    
        except Exception as e:
            logger.error(f"Error in real-time monitoring: {e}")
    
    async def get_system_health(self) -> SystemHealth:
        """Get current system health status"""
        try:
            # Check component health
            components = {
                "behavior_engine": "healthy",
                "alert_manager": "healthy",
                "event_collector": "healthy",
                "risk_scorer": "healthy"
            }
            
            # Get system metrics
            current_time = datetime.utcnow()
            one_hour_ago = current_time - timedelta(hours=1)
            
            # This would typically query actual databases
            metrics = {
                "uptime_hours": 24.0,
                "memory_usage_mb": 512.0,
                "cpu_usage_percent": 15.5,
                "disk_usage_percent": 45.2,
                "active_entities": 150,
                "events_per_second": 25.0
            }
            
            health = SystemHealth(
                status="healthy",
                components=components,
                metrics=metrics,
                active_models=["isolation_forest", "local_outlier_factor", "one_class_svm"],
                data_sources_connected=5,
                events_processed_last_hour=90000,
                alerts_generated_last_hour=12,
                average_processing_time=0.25
            )
            
            return health
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return SystemHealth(
                status="error",
                components={"system": "error"},
                metrics={}
            )
    
    async def get_security_metrics(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> SecurityMetrics:
        """Get security metrics for a time period"""
        try:
            # This would typically query actual databases and metrics storage
            metrics = SecurityMetrics(
                period_start=start_time,
                period_end=end_time,
                total_events_processed=250000,
                total_anomalies_detected=1250,
                total_alerts_generated=89,
                false_positive_rate=0.05,
                mean_time_to_detection=2.5,
                mean_time_to_resolution=25.0,
                high_risk_entities=15,
                coverage_percentage=98.5,
                model_accuracy=0.94
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting security metrics: {e}")
            raise
    
    async def update_entity_baseline(
        self,
        entity_id: str,
        force_rebuild: bool = False
    ):
        """Update behavioral baseline for an entity"""
        try:
            entity = await self._get_entity_by_id(entity_id)
            if not entity:
                raise ValueError(f"Entity {entity_id} not found")
            
            # Get historical events for baseline calculation
            baseline_period_start = datetime.utcnow() - timedelta(days=settings.baseline_training_days)
            historical_events = await self._collect_entity_events(
                entity_id, baseline_period_start, datetime.utcnow()
            )
            
            # Create or update baseline
            await self.behavior_engine._create_baseline(entity)
            
            logger.info(f"Updated baseline for entity {entity_id}")
            
        except Exception as e:
            logger.error(f"Error updating entity baseline: {e}")
            raise
    
    async def train_models(self, training_data_days: int = 30):
        """Retrain ML models with recent data"""
        try:
            logger.info("Starting model training")
            
            # Collect training data
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=training_data_days)
            
            # This would implement actual model training
            # For now, just reinitialize models
            self.behavior_engine._initialize_models()
            
            logger.info("Model training completed")
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            raise
    
    async def _collect_entities(
        self,
        entity_ids: List[str],
        entity_type: Optional[EntityType] = None
    ) -> List[Entity]:
        """Collect entities by IDs and type"""
        entities = []
        
        # This would typically query a database
        # For now, create mock entities
        for entity_id in entity_ids:
            if entity_type == EntityType.USER:
                entity = User(
                    entity_id=entity_id,
                    name=f"User {entity_id}",
                    username=f"user_{entity_id}",
                    baseline_established=True
                )
            elif entity_type == EntityType.DEVICE:
                entity = Device(
                    entity_id=entity_id,
                    name=f"Device {entity_id}",
                    device_id=entity_id,
                    baseline_established=True
                )
            else:
                entity = Entity(
                    entity_id=entity_id,
                    entity_type=entity_type or EntityType.USER,
                    name=f"Entity {entity_id}",
                    baseline_established=True
                )
            
            entities.append(entity)
        
        return entities
    
    async def _collect_events_for_entities(
        self,
        entities: List[Entity],
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, List[BaseEvent]]:
        """Collect events for entities in time range"""
        events_by_entity = {}
        
        for entity in entities:
            events = await self._collect_entity_events(entity.entity_id, start_time, end_time)
            events_by_entity[entity.entity_id] = events
        
        return events_by_entity
    
    async def _collect_entity_events(
        self,
        entity_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[BaseEvent]:
        """Collect events for a specific entity"""
        # This would typically query event databases
        # For now, return empty list
        return []
    
    async def _get_entity_for_event(self, event: BaseEvent) -> Optional[Entity]:
        """Get entity associated with an event"""
        # This would typically look up entity in database
        return None
    
    async def _quick_anomaly_detection(
        self,
        entity: Entity,
        event: BaseEvent
    ) -> List[Any]:
        """Perform quick anomaly detection for real-time processing"""
        # Simplified anomaly detection for real-time use
        return []
    
    async def _get_anomalies_by_ids(self, anomaly_ids: List[Any]) -> List[Any]:
        """Get anomaly objects by their IDs"""
        # This would typically query anomaly storage
        return []
    
    async def _create_risk_alert(
        self,
        entity: Entity,
        risk_score: RiskScore,
        anomalies: List[Any]
    ) -> Alert:
        """Create alert for high-risk entity"""
        severity = AlertSeverity.HIGH if risk_score.risk_level == RiskLevel.HIGH else AlertSeverity.CRITICAL
        
        alert = Alert(
            title=f"High Risk Entity Detected: {entity.name}",
            description=f"Entity {entity.entity_id} has elevated risk score of {risk_score.overall_score:.3f}",
            severity=severity,
            entity_id=entity.entity_id,
            entity_type=entity.entity_type,
            risk_score=risk_score.overall_score,
            evidence={
                "risk_factors": risk_score.risk_factors,
                "anomaly_count": len(anomalies)
            },
            mitigation_suggestions=[
                "Review recent activity",
                "Verify user identity",
                "Monitor closely"
            ]
        )
        
        return alert
    
    async def _create_anomaly_alert(
        self,
        entity: Entity,
        anomaly: Any,
        event: BaseEvent
    ) -> Alert:
        """Create alert for detected anomaly"""
        alert = Alert(
            title=f"Behavioral Anomaly Detected",
            description=f"Anomalous behavior detected for {entity.name}",
            severity=AlertSeverity.MEDIUM,
            entity_id=entity.entity_id,
            entity_type=entity.entity_type,
            risk_score=anomaly.anomaly_score,
            evidence={
                "anomaly_type": str(anomaly.anomaly_type),
                "event_id": event.event_id
            }
        )
        
        return alert
    
    async def _get_entity_by_id(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID"""
        # This would typically query entity database
        return None


# Global UEBA system instance
ueba_system = UEBASystem()


async def main():
    """Example usage of UEBA system"""
    try:
        # Example analysis request
        request = AnalysisRequest(
            entity_ids=["user_001", "user_002"],
            entity_type=EntityType.USER,
            start_time=datetime.utcnow() - timedelta(hours=24),
            end_time=datetime.utcnow(),
            analysis_types=["anomaly_detection", "risk_scoring"]
        )
        
        def progress_callback(message: str, progress: float):
            print(f"Progress: {progress:.1f}% - {message}")
        
        # Run analysis
        response = await ueba_system.analyze_entity_behavior(request, progress_callback)
        
        print(f"\nAnalysis Results:")
        print(f"Status: {response.status}")
        print(f"Processing Time: {response.processing_time:.2f}s")
        print(f"Entities Analyzed: {response.results.get('entities_analyzed', 0)}")
        print(f"Anomalies Detected: {len(response.anomalies)}")
        print(f"Alerts Generated: {len(response.alerts)}")
        
        # Get system health
        health = await ueba_system.get_system_health()
        print(f"\nSystem Status: {health.status}")
        print(f"Events Processed (Last Hour): {health.events_processed_last_hour}")
        print(f"Alerts Generated (Last Hour): {health.alerts_generated_last_hour}")
        
    except Exception as e:
        logger.error(f"Error in main example: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 