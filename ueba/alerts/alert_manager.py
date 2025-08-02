"""
UEBA Alert Management System
Handles alert processing, escalation, and notification
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Callable
from loguru import logger
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import requests
import json

from ..models.schemas import (
    Alert, AlertSeverity, AlertStatus, Entity, RiskLevel
)
from ..config.settings import settings, AlertConfig


class AlertManager:
    """Manages alert processing, escalation, and notifications"""
    
    def __init__(self):
        self.active_alerts = {}
        self.alert_cooldowns = {}
        self.escalation_rules = AlertConfig.ESCALATION_RULES
        self.notification_channels = []
        
        logger.info("Alert Manager initialized")
    
    async def process_alert(self, alert: Alert):
        """
        Process and handle a new alert
        
        Args:
            alert: Alert to process
        """
        try:
            logger.info(f"Processing alert {alert.alert_id}: {alert.title}")
            
            # Check if alert should be suppressed
            if await self._should_suppress_alert(alert):
                logger.info(f"Alert {alert.alert_id} suppressed due to cooldown")
                return
            
            # Store alert
            self.active_alerts[alert.alert_id] = alert
            
            # Set cooldown
            await self._set_alert_cooldown(alert)
            
            # Check for escalation
            if await self._should_escalate_alert(alert):
                await self._escalate_alert(alert)
            
            # Send notifications
            await self._send_notifications(alert)
            
            # Update alert status
            alert.status = AlertStatus.OPEN
            
            logger.info(f"Alert {alert.alert_id} processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing alert {alert.alert_id}: {e}")
    
    async def update_alert_status(
        self,
        alert_id: str,
        status: AlertStatus,
        resolution_notes: Optional[str] = None,
        assigned_to: Optional[str] = None
    ):
        """Update alert status and metadata"""
        try:
            if alert_id not in self.active_alerts:
                logger.warning(f"Alert {alert_id} not found")
                return
            
            alert = self.active_alerts[alert_id]
            alert.status = status
            alert.updated_at = datetime.utcnow()
            
            if resolution_notes:
                alert.resolution_notes = resolution_notes
            
            if assigned_to:
                alert.assigned_to = assigned_to
            
            if status == AlertStatus.RESOLVED:
                alert.resolved_at = datetime.utcnow()
                await self._send_resolution_notification(alert)
            
            logger.info(f"Alert {alert_id} status updated to {status}")
            
        except Exception as e:
            logger.error(f"Error updating alert status: {e}")
    
    async def get_active_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        entity_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Alert]:
        """Get active alerts with optional filters"""
        try:
            alerts = list(self.active_alerts.values())
            
            # Apply filters
            if severity:
                alerts = [a for a in alerts if a.severity == severity]
            
            if entity_id:
                alerts = [a for a in alerts if a.entity_id == entity_id]
            
            # Sort by creation time (newest first)
            alerts.sort(key=lambda x: x.created_at, reverse=True)
            
            return alerts[:limit]
            
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []
    
    async def mark_false_positive(
        self,
        alert_id: str,
        feedback_notes: Optional[str] = None
    ):
        """Mark alert as false positive"""
        try:
            if alert_id not in self.active_alerts:
                logger.warning(f"Alert {alert_id} not found")
                return
            
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.FALSE_POSITIVE
            alert.false_positive_feedback = True
            alert.resolution_notes = feedback_notes or "Marked as false positive"
            alert.resolved_at = datetime.utcnow()
            
            # Learn from false positive to improve future detection
            await self._learn_from_false_positive(alert)
            
            logger.info(f"Alert {alert_id} marked as false positive")
            
        except Exception as e:
            logger.error(f"Error marking false positive: {e}")
    
    async def suppress_alert(
        self,
        alert_id: str,
        suppress_until: datetime,
        reason: str
    ):
        """Suppress alert until specified time"""
        try:
            if alert_id not in self.active_alerts:
                logger.warning(f"Alert {alert_id} not found")
                return
            
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.SUPPRESSED
            alert.suppressed_until = suppress_until
            alert.resolution_notes = f"Suppressed: {reason}"
            
            logger.info(f"Alert {alert_id} suppressed until {suppress_until}")
            
        except Exception as e:
            logger.error(f"Error suppressing alert: {e}")
    
    async def add_notification_channel(
        self,
        channel_type: str,
        config: Dict[str, Any]
    ):
        """Add notification channel"""
        try:
            channel = {
                'type': channel_type,
                'config': config,
                'enabled': True
            }
            
            self.notification_channels.append(channel)
            logger.info(f"Added {channel_type} notification channel")
            
        except Exception as e:
            logger.error(f"Error adding notification channel: {e}")
    
    async def _should_suppress_alert(self, alert: Alert) -> bool:
        """Check if alert should be suppressed due to cooldown"""
        try:
            cooldown_key = f"{alert.entity_id}_{alert.severity.value}"
            
            if cooldown_key in self.alert_cooldowns:
                last_alert_time = self.alert_cooldowns[cooldown_key]
                time_since_last = (datetime.utcnow() - last_alert_time).total_seconds() / 60
                
                if time_since_last < settings.alert_cooldown_minutes:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking alert suppression: {e}")
            return False
    
    async def _set_alert_cooldown(self, alert: Alert):
        """Set cooldown for alert type"""
        try:
            cooldown_key = f"{alert.entity_id}_{alert.severity.value}"
            self.alert_cooldowns[cooldown_key] = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error setting alert cooldown: {e}")
    
    async def _should_escalate_alert(self, alert: Alert) -> bool:
        """Check if alert should be escalated"""
        try:
            # Critical alerts are always escalated immediately
            if alert.severity == AlertSeverity.CRITICAL:
                return self.escalation_rules.get('critical_alert_immediate_escalation', True)
            
            # Check for repeated alerts
            similar_alerts = [
                a for a in self.active_alerts.values()
                if (a.entity_id == alert.entity_id and 
                    a.severity == alert.severity and
                    a.created_at >= datetime.utcnow() - timedelta(hours=24))
            ]
            
            threshold = self.escalation_rules.get('repeated_alerts_threshold', 5)
            return len(similar_alerts) >= threshold
            
        except Exception as e:
            logger.error(f"Error checking escalation: {e}")
            return False
    
    async def _escalate_alert(self, alert: Alert):
        """Escalate alert to higher severity/priority"""
        try:
            alert.escalated = True
            alert.escalated_at = datetime.utcnow()
            
            # Increase severity if possible
            if alert.severity == AlertSeverity.MEDIUM:
                alert.severity = AlertSeverity.HIGH
            elif alert.severity == AlertSeverity.HIGH:
                alert.severity = AlertSeverity.CRITICAL
            
            logger.info(f"Alert {alert.alert_id} escalated to {alert.severity}")
            
            # Send escalation notification
            await self._send_escalation_notification(alert)
            
        except Exception as e:
            logger.error(f"Error escalating alert: {e}")
    
    async def _send_notifications(self, alert: Alert):
        """Send notifications through configured channels"""
        try:
            for channel in self.notification_channels:
                if not channel.get('enabled', False):
                    continue
                
                channel_type = channel['type']
                config = channel['config']
                
                if channel_type == 'email':
                    await self._send_email_notification(alert, config)
                elif channel_type == 'slack':
                    await self._send_slack_notification(alert, config)
                elif channel_type == 'webhook':
                    await self._send_webhook_notification(alert, config)
            
            # Default email notification if configured
            if settings.smtp_server and settings.alert_email_to:
                await self._send_default_email_notification(alert)
            
            # Default Slack notification if configured
            if settings.slack_webhook_url:
                await self._send_default_slack_notification(alert)
                
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
    
    async def _send_email_notification(self, alert: Alert, config: Dict[str, Any]):
        """Send email notification"""
        try:
            smtp_server = config.get('smtp_server', settings.smtp_server)
            smtp_port = config.get('smtp_port', settings.smtp_port)
            username = config.get('username', settings.smtp_username)
            password = config.get('password', settings.smtp_password)
            from_email = config.get('from_email', settings.alert_email_from)
            to_emails = config.get('to_emails', settings.alert_email_to)
            
            if not all([smtp_server, username, password, from_email, to_emails]):
                logger.warning("Email configuration incomplete")
                return
            
            # Create message
            msg = MimeMultipart()
            msg['From'] = from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = f"[{alert.severity.upper()}] {alert.title}"
            
            # Create email body
            body = self._create_email_body(alert)
            msg.attach(MimeText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)
            
            logger.info(f"Email notification sent for alert {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    async def _send_slack_notification(self, alert: Alert, config: Dict[str, Any]):
        """Send Slack notification"""
        try:
            webhook_url = config.get('webhook_url', settings.slack_webhook_url)
            channel = config.get('channel', settings.slack_channel)
            
            if not webhook_url:
                logger.warning("Slack webhook URL not configured")
                return
            
            # Create Slack message
            color = self._get_alert_color(alert.severity)
            
            payload = {
                "channel": channel,
                "attachments": [{
                    "color": color,
                    "title": alert.title,
                    "text": alert.description,
                    "fields": [
                        {
                            "title": "Entity",
                            "value": alert.entity_id,
                            "short": True
                        },
                        {
                            "title": "Severity",
                            "value": alert.severity.upper(),
                            "short": True
                        },
                        {
                            "title": "Risk Score",
                            "value": f"{alert.risk_score:.3f}",
                            "short": True
                        },
                        {
                            "title": "Time",
                            "value": alert.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "short": True
                        }
                    ],
                    "footer": "UEBA System",
                    "ts": int(alert.created_at.timestamp())
                }]
            }
            
            # Send to Slack
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Slack notification sent for alert {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
    
    async def _send_webhook_notification(self, alert: Alert, config: Dict[str, Any]):
        """Send webhook notification"""
        try:
            webhook_url = config['url']
            headers = config.get('headers', {'Content-Type': 'application/json'})
            
            # Create webhook payload
            payload = {
                "alert_id": alert.alert_id,
                "title": alert.title,
                "description": alert.description,
                "severity": alert.severity,
                "entity_id": alert.entity_id,
                "entity_type": alert.entity_type,
                "risk_score": alert.risk_score,
                "created_at": alert.created_at.isoformat(),
                "evidence": alert.evidence
            }
            
            # Send webhook
            response = requests.post(webhook_url, json=payload, headers=headers)
            response.raise_for_status()
            
            logger.info(f"Webhook notification sent for alert {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")
    
    async def _send_default_email_notification(self, alert: Alert):
        """Send default email notification"""
        config = {
            'smtp_server': settings.smtp_server,
            'smtp_port': settings.smtp_port,
            'username': settings.smtp_username,
            'password': settings.smtp_password,
            'from_email': settings.alert_email_from,
            'to_emails': settings.alert_email_to
        }
        
        await self._send_email_notification(alert, config)
    
    async def _send_default_slack_notification(self, alert: Alert):
        """Send default Slack notification"""
        config = {
            'webhook_url': settings.slack_webhook_url,
            'channel': settings.slack_channel
        }
        
        await self._send_slack_notification(alert, config)
    
    async def _send_escalation_notification(self, alert: Alert):
        """Send notification for escalated alert"""
        # Create escalation-specific message
        original_title = alert.title
        alert.title = f"[ESCALATED] {original_title}"
        alert.description = f"ESCALATED: {alert.description}"
        
        await self._send_notifications(alert)
        
        # Restore original title
        alert.title = original_title
    
    async def _send_resolution_notification(self, alert: Alert):
        """Send notification when alert is resolved"""
        try:
            # Only send resolution notifications for high severity alerts
            if alert.severity not in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                return
            
            # Create resolution message
            resolution_alert = Alert(
                title=f"[RESOLVED] {alert.title}",
                description=f"Alert has been resolved: {alert.resolution_notes}",
                severity=AlertSeverity.LOW,
                entity_id=alert.entity_id,
                entity_type=alert.entity_type,
                risk_score=0.0
            )
            
            await self._send_notifications(resolution_alert)
            
        except Exception as e:
            logger.error(f"Error sending resolution notification: {e}")
    
    async def _learn_from_false_positive(self, alert: Alert):
        """Learn from false positive to improve detection"""
        try:
            # This would typically update ML models or detection rules
            # For now, just log the false positive
            logger.info(f"Learning from false positive: {alert.alert_id}")
            
            # Could implement:
            # - Update anomaly detection thresholds
            # - Adjust risk scoring weights
            # - Train ML models with corrected labels
            
        except Exception as e:
            logger.error(f"Error learning from false positive: {e}")
    
    def _create_email_body(self, alert: Alert) -> str:
        """Create HTML email body for alert"""
        return f"""
        <html>
        <body>
            <h2 style="color: {self._get_alert_color(alert.severity)};">{alert.title}</h2>
            
            <p><strong>Description:</strong> {alert.description}</p>
            
            <table border="1" cellpadding="5" cellspacing="0">
                <tr><td><strong>Alert ID</strong></td><td>{alert.alert_id}</td></tr>
                <tr><td><strong>Severity</strong></td><td>{alert.severity.upper()}</td></tr>
                <tr><td><strong>Entity ID</strong></td><td>{alert.entity_id}</td></tr>
                <tr><td><strong>Entity Type</strong></td><td>{alert.entity_type}</td></tr>
                <tr><td><strong>Risk Score</strong></td><td>{alert.risk_score:.3f}</td></tr>
                <tr><td><strong>Created At</strong></td><td>{alert.created_at.strftime("%Y-%m-%d %H:%M:%S")}</td></tr>
            </table>
            
            <h3>Evidence:</h3>
            <pre>{json.dumps(alert.evidence, indent=2)}</pre>
            
            <h3>Mitigation Suggestions:</h3>
            <ul>
                {"".join(f"<li>{suggestion}</li>" for suggestion in alert.mitigation_suggestions)}
            </ul>
            
            <p><em>Generated by UEBA System</em></p>
        </body>
        </html>
        """
    
    def _get_alert_color(self, severity: AlertSeverity) -> str:
        """Get color for alert severity"""
        colors = {
            AlertSeverity.LOW: "#36a64f",      # Green
            AlertSeverity.MEDIUM: "#ff9500",   # Orange
            AlertSeverity.HIGH: "#ff4500",     # Red-Orange
            AlertSeverity.CRITICAL: "#ff0000"  # Red
        }
        return colors.get(severity, "#808080") 