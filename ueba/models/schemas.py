"""
Pydantic models for UEBA (User Entity Behavior Analytics) system
"""
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4
import ipaddress


# Enums
class EntityType(str, Enum):
    """Entity types in the system"""
    USER = "user"
    DEVICE = "device"
    APPLICATION = "application"
    SERVICE_ACCOUNT = "service_account"
    NETWORK_RESOURCE = "network_resource"


class EventType(str, Enum):
    """Types of events monitored"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    NETWORK_ACCESS = "network_access"
    APPLICATION_USAGE = "application_usage"
    FILE_ACCESS = "file_access"
    API_CALL = "api_call"
    SYSTEM_EVENT = "system_event"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status options"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    SUPPRESSED = "suppressed"


class AnomalyType(str, Enum):
    """Types of anomalies detected"""
    TIME_ANOMALY = "time_anomaly"
    LOCATION_ANOMALY = "location_anomaly"
    ACCESS_ANOMALY = "access_anomaly"
    VOLUME_ANOMALY = "volume_anomaly"
    PATTERN_ANOMALY = "pattern_anomaly"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"


class RiskLevel(str, Enum):
    """Risk levels for entities and activities"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


# Base Models
class BaseUEBAModel(BaseModel):
    """Base model with common fields"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


# Entity Models
class Entity(BaseUEBAModel):
    """Base entity model"""
    entity_id: str
    entity_type: EntityType
    name: str
    description: Optional[str] = None
    attributes: Dict[str, Any] = {}
    risk_factors: Dict[str, float] = {}
    baseline_established: bool = False
    baseline_created_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    is_active: bool = True
    tags: List[str] = []


class User(Entity):
    """User entity model"""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    manager: Optional[str] = None
    employee_id: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = None
    is_privileged: bool = False
    access_level: int = 1
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    
    def __init__(self, **data):
        super().__init__(**data)
        self.entity_type = EntityType.USER


class Device(Entity):
    """Device entity model"""
    device_id: str
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    os_type: Optional[str] = None
    os_version: Optional[str] = None
    device_type: Optional[str] = None
    owner: Optional[str] = None
    location: Optional[str] = None
    is_managed: bool = True
    is_trusted: bool = False
    last_seen: Optional[datetime] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        self.entity_type = EntityType.DEVICE
    
    @validator('ip_address')
    def validate_ip_address(cls, v):
        if v is not None:
            try:
                ipaddress.ip_address(v)
            except ValueError:
                raise ValueError('Invalid IP address format')
        return v


class Application(Entity):
    """Application entity model"""
    app_id: str
    app_name: str
    version: Optional[str] = None
    vendor: Optional[str] = None
    criticality: str = "medium"
    data_classification: Optional[str] = None
    owner: Optional[str] = None
    url: Optional[str] = None
    is_external_facing: bool = False
    contains_pii: bool = False
    contains_financial_data: bool = False
    
    def __init__(self, **data):
        super().__init__(**data)
        self.entity_type = EntityType.APPLICATION


# Event Models
class BaseEvent(BaseUEBAModel):
    """Base event model"""
    event_id: str
    event_type: EventType
    timestamp: datetime
    source_ip: Optional[str] = None
    source_location: Optional[Dict[str, Any]] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


class AuthenticationEvent(BaseEvent):
    """Authentication event model"""
    user_id: str
    username: str
    authentication_method: str
    result: str  # success, failure, timeout
    failure_reason: Optional[str] = None
    device_id: Optional[str] = None
    application_id: Optional[str] = None
    mfa_used: bool = False
    risk_score: Optional[float] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        self.event_type = EventType.AUTHENTICATION


class DataAccessEvent(BaseEvent):
    """Data access event model"""
    user_id: str
    resource_id: str
    resource_type: str
    action: str  # read, write, delete, etc.
    data_classification: Optional[str] = None
    bytes_accessed: Optional[int] = None
    records_accessed: Optional[int] = None
    access_method: Optional[str] = None
    result: str  # allowed, denied
    
    def __init__(self, **data):
        super().__init__(**data)
        self.event_type = EventType.DATA_ACCESS


class NetworkAccessEvent(BaseEvent):
    """Network access event model"""
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    destination_ip: str
    destination_port: int
    protocol: str
    bytes_sent: Optional[int] = None
    bytes_received: Optional[int] = None
    duration: Optional[float] = None
    result: str
    
    def __init__(self, **data):
        super().__init__(**data)
        self.event_type = EventType.NETWORK_ACCESS


# Analytics Models
class BehaviorBaseline(BaseUEBAModel):
    """Baseline behavior model for entities"""
    entity_id: str
    entity_type: EntityType
    baseline_period_start: datetime
    baseline_period_end: datetime
    features: Dict[str, Any]
    statistical_measures: Dict[str, float]
    pattern_signatures: List[Dict[str, Any]] = []
    is_valid: bool = True
    confidence_score: float = 0.0


class AnomalyDetection(BaseUEBAModel):
    """Anomaly detection result"""
    entity_id: str
    event_id: Optional[str] = None
    anomaly_type: AnomalyType
    anomaly_score: float
    confidence: float
    threshold: float
    baseline_id: Optional[UUID] = None
    features_analyzed: Dict[str, Any]
    deviation_details: Dict[str, float]
    temporal_context: Optional[Dict[str, Any]] = None
    
    @validator('anomaly_score', 'confidence')
    def validate_scores(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Score must be between 0 and 1')
        return v


class RiskScore(BaseUEBAModel):
    """Risk score calculation for entities"""
    entity_id: str
    entity_type: EntityType
    overall_score: float
    risk_level: RiskLevel
    risk_factors: Dict[str, float]
    contributing_events: List[str] = []
    calculation_method: str = "weighted_average"
    decay_applied: bool = False
    last_calculated: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('overall_score')
    def validate_score(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Risk score must be between 0 and 1')
        return v


# Alert Models
class Alert(BaseUEBAModel):
    """Security alert model"""
    alert_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus = AlertStatus.OPEN
    entity_id: str
    entity_type: EntityType
    anomaly_ids: List[UUID] = []
    risk_score: float
    evidence: Dict[str, Any] = {}
    mitigation_suggestions: List[str] = []
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    false_positive_feedback: Optional[bool] = None
    escalated: bool = False
    escalated_at: Optional[datetime] = None
    suppressed_until: Optional[datetime] = None


# Analysis Models
class UserBehaviorAnalysis(BaseUEBAModel):
    """User behavior analysis result"""
    user_id: str
    analysis_period_start: datetime
    analysis_period_end: datetime
    activity_summary: Dict[str, Any]
    login_patterns: Dict[str, Any]
    access_patterns: Dict[str, Any]
    geographic_patterns: Dict[str, Any]
    temporal_patterns: Dict[str, Any]
    anomalies_detected: List[UUID] = []
    risk_indicators: List[str] = []
    behavioral_changes: List[Dict[str, Any]] = []


class EntityRelationship(BaseUEBAModel):
    """Relationship between entities"""
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    strength: float  # 0-1
    frequency: int
    last_interaction: datetime
    context: Dict[str, Any] = {}
    
    @validator('strength')
    def validate_strength(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Relationship strength must be between 0 and 1')
        return v


# Reporting Models
class SecurityMetrics(BaseUEBAModel):
    """Security metrics and KPIs"""
    period_start: datetime
    period_end: datetime
    total_events_processed: int
    total_anomalies_detected: int
    total_alerts_generated: int
    false_positive_rate: float
    mean_time_to_detection: float
    mean_time_to_resolution: float
    high_risk_entities: int
    coverage_percentage: float
    model_accuracy: Optional[float] = None


class ThreatIntelligence(BaseUEBAModel):
    """Threat intelligence integration"""
    indicator_id: str
    indicator_type: str  # ip, domain, hash, etc.
    indicator_value: str
    threat_type: str
    confidence: float
    severity: AlertSeverity
    source: str
    first_seen: datetime
    last_seen: datetime
    tags: List[str] = []
    context: Dict[str, Any] = {}


# API Models
class AnalysisRequest(BaseModel):
    """Request for behavior analysis"""
    entity_ids: List[str]
    entity_type: Optional[EntityType] = None
    start_time: datetime
    end_time: datetime
    analysis_types: List[str] = ["anomaly_detection", "risk_scoring"]
    options: Dict[str, Any] = {}


class AnalysisResponse(BaseModel):
    """Response from behavior analysis"""
    request_id: UUID
    status: str
    results: Dict[str, Any]
    anomalies: List[AnomalyDetection] = []
    risk_scores: List[RiskScore] = []
    alerts: List[Alert] = []
    processing_time: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AlertQuery(BaseModel):
    """Query parameters for alerts"""
    severity: Optional[List[AlertSeverity]] = None
    status: Optional[List[AlertStatus]] = None
    entity_ids: Optional[List[str]] = None
    entity_types: Optional[List[EntityType]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)


class SystemHealth(BaseModel):
    """System health status"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    components: Dict[str, str] = {}
    metrics: Dict[str, float] = {}
    active_models: List[str] = []
    data_sources_connected: int = 0
    events_processed_last_hour: int = 0
    alerts_generated_last_hour: int = 0
    average_processing_time: float = 0.0


# Configuration Models
class ModelConfiguration(BaseModel):
    """ML model configuration"""
    model_name: str
    model_type: str
    version: str
    parameters: Dict[str, Any]
    training_data_period: int  # days
    retrain_frequency: int  # hours
    feature_importance: Dict[str, float] = {}
    performance_metrics: Dict[str, float] = {}
    last_trained: Optional[datetime] = None
    is_active: bool = True


class DataSourceConfiguration(BaseModel):
    """Data source configuration"""
    source_id: str
    source_name: str
    source_type: str
    connection_string: str
    credentials: Optional[Dict[str, str]] = None
    polling_interval: int = 300  # seconds
    data_format: str = "json"
    field_mappings: Dict[str, str] = {}
    filters: List[Dict[str, Any]] = []
    is_enabled: bool = True
    last_successful_collection: Optional[datetime] = None


# Feature Engineering Models
class FeatureVector(BaseModel):
    """Feature vector for ML models"""
    entity_id: str
    timestamp: datetime
    features: Dict[str, float]
    feature_version: str = "1.0"
    window_size: str = "24h"  # time window for feature calculation


class BehaviorProfile(BaseModel):
    """Behavioral profile for an entity"""
    entity_id: str
    entity_type: EntityType
    profile_version: str = "1.0"
    temporal_patterns: Dict[str, Any] = {}
    access_patterns: Dict[str, Any] = {}
    location_patterns: Dict[str, Any] = {}
    interaction_patterns: Dict[str, Any] = {}
    risk_indicators: List[str] = []
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = 0.0 