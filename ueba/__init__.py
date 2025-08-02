"""
UEBA (User Entity Behavior Analytics) System

A comprehensive behavioral analytics system for detecting anomalies,
assessing risks, and generating security alerts based on user and
entity behavior patterns.
"""

from .main import ueba_system, UEBASystem
from .models.schemas import (
    Entity, User, Device, Application,
    BaseEvent, AuthenticationEvent, DataAccessEvent, NetworkAccessEvent,
    AnalysisRequest, AnalysisResponse,
    Alert, AlertSeverity, AlertStatus,
    RiskScore, RiskLevel,
    AnomalyDetection, AnomalyType,
    EntityType, EventType,
    SystemHealth
)
from .config.settings import settings

__version__ = "1.0.0"
__author__ = "UEBA Analytics Team"
__email__ = "support@uebaanalytics.com"

__all__ = [
    # Main system
    "ueba_system",
    "UEBASystem",
    
    # Core entities
    "Entity",
    "User", 
    "Device",
    "Application",
    
    # Events
    "BaseEvent",
    "AuthenticationEvent",
    "DataAccessEvent", 
    "NetworkAccessEvent",
    
    # API models
    "AnalysisRequest",
    "AnalysisResponse",
    
    # Alerts
    "Alert",
    "AlertSeverity",
    "AlertStatus",
    
    # Risk scoring
    "RiskScore",
    "RiskLevel",
    
    # Anomaly detection
    "AnomalyDetection",
    "AnomalyType",
    
    # Enums
    "EntityType",
    "EventType",
    
    # System
    "SystemHealth",
    "settings"
] 