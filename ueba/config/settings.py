"""
UEBA (User Entity Behavior Analytics) System Configuration
"""
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseSettings, Field
from datetime import timedelta


class UEBASettings(BaseSettings):
    """Main configuration for UEBA system"""
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8002, env="API_PORT")
    api_debug: bool = Field(default=False, env="API_DEBUG")
    api_workers: int = Field(default=4, env="API_WORKERS")
    
    # Security
    secret_key: str = Field(default="ueba-analytics-secret", env="SECRET_KEY")
    jwt_secret: str = Field(default="jwt-secret-key", env="JWT_SECRET")
    jwt_expiry_hours: int = Field(default=24, env="JWT_EXPIRY_HOURS")
    allowed_origins: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    
    # Database Configuration
    primary_database_url: str = Field(default="postgresql://localhost/ueba", env="PRIMARY_DATABASE_URL")
    timeseries_database_url: str = Field(default="influxdb://localhost:8086", env="TIMESERIES_DATABASE_URL")
    graph_database_url: str = Field(default="neo4j://localhost:7687", env="GRAPH_DATABASE_URL")
    cache_redis_url: str = Field(default="redis://localhost:6379/0", env="CACHE_REDIS_URL")
    session_redis_url: str = Field(default="redis://localhost:6379/1", env="SESSION_REDIS_URL")
    
    # Elasticsearch Configuration
    elasticsearch_hosts: List[str] = Field(default=["localhost:9200"], env="ELASTICSEARCH_HOSTS")
    elasticsearch_index_prefix: str = Field(default="ueba", env="ELASTICSEARCH_INDEX_PREFIX")
    
    # Stream Processing
    kafka_bootstrap_servers: List[str] = Field(default=["localhost:9092"], env="KAFKA_BOOTSTRAP_SERVERS")
    kafka_group_id: str = Field(default="ueba-analytics", env="KAFKA_GROUP_ID")
    
    # Data Collection
    data_retention_days: int = Field(default=90, env="DATA_RETENTION_DAYS")
    batch_processing_interval: int = Field(default=300, env="BATCH_PROCESSING_INTERVAL")  # seconds
    real_time_processing_enabled: bool = Field(default=True, env="REAL_TIME_PROCESSING_ENABLED")
    
    # Analytics Configuration
    baseline_training_days: int = Field(default=30, env="BASELINE_TRAINING_DAYS")
    anomaly_detection_sensitivity: float = Field(default=0.05, env="ANOMALY_DETECTION_SENSITIVITY")
    risk_score_threshold: float = Field(default=0.7, env="RISK_SCORE_THRESHOLD")
    
    # Machine Learning
    ml_model_retrain_interval_hours: int = Field(default=24, env="ML_MODEL_RETRAIN_INTERVAL_HOURS")
    ml_feature_window_hours: int = Field(default=24, env="ML_FEATURE_WINDOW_HOURS")
    ml_model_storage_path: str = Field(default="models/", env="ML_MODEL_STORAGE_PATH")
    
    # Performance Configuration
    max_concurrent_analyses: int = Field(default=10, env="MAX_CONCURRENT_ANALYSES")
    analysis_timeout_seconds: int = Field(default=300, env="ANALYSIS_TIMEOUT_SECONDS")
    data_processing_batch_size: int = Field(default=1000, env="DATA_PROCESSING_BATCH_SIZE")
    
    # Alerting
    alert_cooldown_minutes: int = Field(default=60, env="ALERT_COOLDOWN_MINUTES")
    max_alerts_per_hour: int = Field(default=100, env="MAX_ALERTS_PER_HOUR")
    
    # Slack Integration
    slack_webhook_url: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
    slack_channel: str = Field(default="#security-alerts", env="SLACK_CHANNEL")
    
    # Email Alerts
    smtp_server: Optional[str] = Field(default=None, env="SMTP_SERVER")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    alert_email_from: str = Field(default="alerts@company.com", env="ALERT_EMAIL_FROM")
    alert_email_to: List[str] = Field(default=["security@company.com"], env="ALERT_EMAIL_TO")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/ueba.log", env="LOG_FILE")
    log_rotation: str = Field(default="1 day", env="LOG_ROTATION")
    log_retention: str = Field(default="30 days", env="LOG_RETENTION")
    
    # Monitoring
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    prometheus_port: int = Field(default=8003, env="PROMETHEUS_PORT")
    health_check_interval: int = Field(default=60, env="HEALTH_CHECK_INTERVAL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class DataSourceConfig:
    """Configuration for different data sources"""
    
    # Authentication Logs
    AUTH_LOG_SOURCES = [
        "active_directory",
        "ldap",
        "sso_providers",
        "vpn_logs",
        "application_auth"
    ]
    
    # Network Data Sources
    NETWORK_SOURCES = [
        "firewall_logs",
        "proxy_logs",
        "dns_logs",
        "netflow_data",
        "packet_capture"
    ]
    
    # Application Sources
    APPLICATION_SOURCES = [
        "web_applications",
        "database_access",
        "api_gateways",
        "file_access",
        "email_systems"
    ]
    
    # Endpoint Sources
    ENDPOINT_SOURCES = [
        "endpoint_agents",
        "antivirus_logs",
        "system_events",
        "process_monitoring",
        "file_integrity"
    ]


class AnalyticsConfig:
    """Analytics and ML model configuration"""
    
    # Risk Score Components
    RISK_FACTORS = {
        "time_anomaly": 0.2,
        "location_anomaly": 0.25,
        "access_anomaly": 0.2,
        "volume_anomaly": 0.15,
        "pattern_anomaly": 0.2
    }
    
    # Anomaly Detection Models
    ANOMALY_MODELS = {
        "isolation_forest": {
            "contamination": 0.1,
            "n_estimators": 100,
            "random_state": 42
        },
        "local_outlier_factor": {
            "n_neighbors": 20,
            "contamination": 0.1
        },
        "one_class_svm": {
            "nu": 0.1,
            "kernel": "rbf",
            "gamma": "scale"
        }
    }
    
    # Feature Engineering
    FEATURE_WINDOWS = {
        "short_term": "1h",
        "medium_term": "24h",
        "long_term": "7d"
    }
    
    # Baseline Behavior Thresholds
    BASELINE_THRESHOLDS = {
        "login_frequency_std_multiplier": 3.0,
        "access_pattern_similarity_threshold": 0.8,
        "geographic_distance_km": 500,
        "time_deviation_hours": 4
    }


class AlertConfig:
    """Alert configuration and thresholds"""
    
    # Alert Severity Levels
    SEVERITY_LEVELS = {
        "LOW": {"score_range": (0.3, 0.5), "priority": 3},
        "MEDIUM": {"score_range": (0.5, 0.7), "priority": 2},
        "HIGH": {"score_range": (0.7, 0.9), "priority": 1},
        "CRITICAL": {"score_range": (0.9, 1.0), "priority": 0}
    }
    
    # Alert Types
    ALERT_TYPES = [
        "unusual_login_time",
        "impossible_travel",
        "privilege_escalation",
        "data_exfiltration",
        "anomalous_access_pattern",
        "suspicious_api_usage",
        "dormant_account_activity",
        "brute_force_attempt",
        "lateral_movement",
        "insider_threat_indicator"
    ]
    
    # Auto-escalation Rules
    ESCALATION_RULES = {
        "repeated_alerts_threshold": 5,
        "escalation_time_window_hours": 24,
        "critical_alert_immediate_escalation": True
    }


class EntityConfig:
    """Entity classification and monitoring configuration"""
    
    # Entity Types
    ENTITY_TYPES = {
        "user": {
            "attributes": ["department", "role", "manager", "location"],
            "risk_factors": ["privileged_access", "data_access_level", "travel_frequency"]
        },
        "device": {
            "attributes": ["os_type", "device_type", "owner", "location"],
            "risk_factors": ["admin_access", "mobile_device", "external_device"]
        },
        "application": {
            "attributes": ["criticality", "data_classification", "owner"],
            "risk_factors": ["external_facing", "contains_pii", "financial_data"]
        },
        "service_account": {
            "attributes": ["purpose", "owner", "permissions"],
            "risk_factors": ["elevated_privileges", "external_access", "age"]
        }
    }
    
    # Monitoring Priorities
    HIGH_PRIORITY_ENTITIES = [
        "privileged_users",
        "service_accounts",
        "external_devices",
        "critical_applications"
    ]


class MetricsConfig:
    """Metrics and KPI configuration"""
    
    # Performance Metrics
    PERFORMANCE_METRICS = [
        "detection_accuracy",
        "false_positive_rate",
        "mean_time_to_detection",
        "alert_resolution_time",
        "model_drift_score"
    ]
    
    # Business Metrics
    BUSINESS_METRICS = [
        "security_incidents_prevented",
        "compliance_score",
        "risk_reduction_percentage",
        "analyst_efficiency"
    ]
    
    # System Metrics
    SYSTEM_METRICS = [
        "data_processing_throughput",
        "model_inference_time",
        "storage_utilization",
        "api_response_time"
    ]


# Create global settings instance
settings = UEBASettings()

# Export commonly used configurations
__all__ = [
    "settings",
    "DataSourceConfig",
    "AnalyticsConfig", 
    "AlertConfig",
    "EntityConfig",
    "MetricsConfig"
] 