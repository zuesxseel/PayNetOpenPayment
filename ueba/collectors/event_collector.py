"""
UEBA Event Collection System
Collects and normalizes events from various data sources
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, AsyncGenerator
from loguru import logger
import pandas as pd
from pathlib import Path

from ..models.schemas import (
    BaseEvent, AuthenticationEvent, DataAccessEvent, NetworkAccessEvent,
    Entity, EntityType, EventType
)
from ..config.settings import settings, DataSourceConfig


class EventCollector:
    """Collects events from various data sources"""
    
    def __init__(self):
        self.data_sources = {}
        self.event_buffer = []
        self.collection_stats = {}
        
        logger.info("Event Collector initialized")
    
    async def register_data_source(
        self,
        source_id: str,
        source_type: str,
        connection_config: Dict[str, Any]
    ):
        """Register a new data source for event collection"""
        try:
            source = {
                'id': source_id,
                'type': source_type,
                'config': connection_config,
                'last_collection': None,
                'events_collected': 0,
                'enabled': True
            }
            
            self.data_sources[source_id] = source
            logger.info(f"Registered data source: {source_id} ({source_type})")
            
        except Exception as e:
            logger.error(f"Error registering data source {source_id}: {e}")
    
    async def collect_events(
        self,
        start_time: datetime,
        end_time: datetime,
        entity_ids: Optional[List[str]] = None,
        event_types: Optional[List[EventType]] = None
    ) -> List[BaseEvent]:
        """
        Collect events from all registered data sources
        
        Args:
            start_time: Start of collection period
            end_time: End of collection period
            entity_ids: Optional filter by entity IDs
            event_types: Optional filter by event types
            
        Returns:
            List of collected and normalized events
        """
        try:
            logger.info(f"Collecting events from {start_time} to {end_time}")
            
            all_events = []
            
            # Collect from each data source
            for source_id, source in self.data_sources.items():
                if not source.get('enabled', True):
                    continue
                
                try:
                    events = await self._collect_from_source(
                        source, start_time, end_time, entity_ids, event_types
                    )
                    all_events.extend(events)
                    
                    # Update collection stats
                    source['last_collection'] = datetime.utcnow()
                    source['events_collected'] += len(events)
                    
                    logger.info(f"Collected {len(events)} events from {source_id}")
                    
                except Exception as e:
                    logger.error(f"Error collecting from source {source_id}: {e}")
            
            # Deduplicate and sort events
            deduplicated_events = await self._deduplicate_events(all_events)
            sorted_events = sorted(deduplicated_events, key=lambda x: x.timestamp)
            
            logger.info(f"Total events collected: {len(sorted_events)}")
            return sorted_events
            
        except Exception as e:
            logger.error(f"Error collecting events: {e}")
            return []
    
    async def collect_real_time_events(
        self,
        source_ids: Optional[List[str]] = None
    ) -> AsyncGenerator[List[BaseEvent], None]:
        """
        Collect events in real-time from streaming sources
        
        Args:
            source_ids: Optional list of source IDs to collect from
            
        Yields:
            Batches of real-time events
        """
        try:
            logger.info("Starting real-time event collection")
            
            # Filter sources
            sources_to_monitor = {}
            for source_id, source in self.data_sources.items():
                if source_ids is None or source_id in source_ids:
                    if source.get('enabled', True) and source['type'] in ['kafka', 'websocket', 'syslog']:
                        sources_to_monitor[source_id] = source
            
            if not sources_to_monitor:
                logger.warning("No real-time sources available")
                return
            
            # Start collection from streaming sources
            while True:
                batch_events = []
                
                for source_id, source in sources_to_monitor.items():
                    try:
                        events = await self._collect_real_time_from_source(source)
                        batch_events.extend(events)
                    except Exception as e:
                        logger.error(f"Error collecting real-time events from {source_id}: {e}")
                
                if batch_events:
                    yield batch_events
                
                # Wait before next collection
                await asyncio.sleep(1.0)
                
        except Exception as e:
            logger.error(f"Error in real-time event collection: {e}")
    
    async def collect_entity_events(
        self,
        entity_id: str,
        start_time: datetime,
        end_time: datetime,
        event_types: Optional[List[EventType]] = None
    ) -> List[BaseEvent]:
        """Collect events for a specific entity"""
        try:
            # Collect all events and filter by entity
            all_events = await self.collect_events(start_time, end_time, [entity_id], event_types)
            
            # Filter events that involve this entity
            entity_events = []
            for event in all_events:
                if self._event_involves_entity(event, entity_id):
                    entity_events.append(event)
            
            logger.info(f"Collected {len(entity_events)} events for entity {entity_id}")
            return entity_events
            
        except Exception as e:
            logger.error(f"Error collecting events for entity {entity_id}: {e}")
            return []
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            stats = {
                'total_sources': len(self.data_sources),
                'enabled_sources': sum(1 for s in self.data_sources.values() if s.get('enabled', True)),
                'total_events_collected': sum(s.get('events_collected', 0) for s in self.data_sources.values()),
                'sources': {}
            }
            
            for source_id, source in self.data_sources.items():
                stats['sources'][source_id] = {
                    'type': source['type'],
                    'enabled': source.get('enabled', True),
                    'events_collected': source.get('events_collected', 0),
                    'last_collection': source.get('last_collection'),
                    'status': 'healthy' if source.get('enabled', True) else 'disabled'
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    async def _collect_from_source(
        self,
        source: Dict[str, Any],
        start_time: datetime,
        end_time: datetime,
        entity_ids: Optional[List[str]],
        event_types: Optional[List[EventType]]
    ) -> List[BaseEvent]:
        """Collect events from a specific data source"""
        source_type = source['type']
        
        if source_type == 'database':
            return await self._collect_from_database(source, start_time, end_time, entity_ids, event_types)
        elif source_type == 'file':
            return await self._collect_from_file(source, start_time, end_time, entity_ids, event_types)
        elif source_type == 'api':
            return await self._collect_from_api(source, start_time, end_time, entity_ids, event_types)
        elif source_type == 'syslog':
            return await self._collect_from_syslog(source, start_time, end_time, entity_ids, event_types)
        else:
            logger.warning(f"Unsupported source type: {source_type}")
            return []
    
    async def _collect_from_database(
        self,
        source: Dict[str, Any],
        start_time: datetime,
        end_time: datetime,
        entity_ids: Optional[List[str]],
        event_types: Optional[List[EventType]]
    ) -> List[BaseEvent]:
        """Collect events from database source"""
        try:
            # This would implement actual database connection and queries
            # For now, return mock events
            mock_events = self._generate_mock_events(start_time, end_time, entity_ids, 10)
            return mock_events
            
        except Exception as e:
            logger.error(f"Error collecting from database source: {e}")
            return []
    
    async def _collect_from_file(
        self,
        source: Dict[str, Any],
        start_time: datetime,
        end_time: datetime,
        entity_ids: Optional[List[str]],
        event_types: Optional[List[EventType]]
    ) -> List[BaseEvent]:
        """Collect events from file source"""
        try:
            file_path = source['config'].get('file_path')
            if not file_path or not Path(file_path).exists():
                logger.warning(f"File not found: {file_path}")
                return []
            
            # Read and parse file
            events = []
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        event_data = json.loads(line.strip())
                        event = await self._normalize_event(event_data, source)
                        
                        # Filter by time range
                        if start_time <= event.timestamp <= end_time:
                            # Filter by entity IDs if specified
                            if entity_ids is None or self._event_involves_entities(event, entity_ids):
                                events.append(event)
                                
                    except json.JSONDecodeError:
                        continue
            
            return events
            
        except Exception as e:
            logger.error(f"Error collecting from file source: {e}")
            return []
    
    async def _collect_from_api(
        self,
        source: Dict[str, Any],
        start_time: datetime,
        end_time: datetime,
        entity_ids: Optional[List[str]],
        event_types: Optional[List[EventType]]
    ) -> List[BaseEvent]:
        """Collect events from API source"""
        try:
            # This would implement actual API calls
            # For now, return mock events
            mock_events = self._generate_mock_events(start_time, end_time, entity_ids, 5)
            return mock_events
            
        except Exception as e:
            logger.error(f"Error collecting from API source: {e}")
            return []
    
    async def _collect_from_syslog(
        self,
        source: Dict[str, Any],
        start_time: datetime,
        end_time: datetime,
        entity_ids: Optional[List[str]],
        event_types: Optional[List[EventType]]
    ) -> List[BaseEvent]:
        """Collect events from syslog source"""
        try:
            # This would implement actual syslog parsing
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Error collecting from syslog source: {e}")
            return []
    
    async def _collect_real_time_from_source(self, source: Dict[str, Any]) -> List[BaseEvent]:
        """Collect real-time events from streaming source"""
        try:
            source_type = source['type']
            
            if source_type == 'kafka':
                return await self._collect_from_kafka_stream(source)
            elif source_type == 'websocket':
                return await self._collect_from_websocket_stream(source)
            elif source_type == 'syslog':
                return await self._collect_from_syslog_stream(source)
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error collecting real-time events: {e}")
            return []
    
    async def _collect_from_kafka_stream(self, source: Dict[str, Any]) -> List[BaseEvent]:
        """Collect events from Kafka stream"""
        # This would implement actual Kafka consumer
        return []
    
    async def _collect_from_websocket_stream(self, source: Dict[str, Any]) -> List[BaseEvent]:
        """Collect events from WebSocket stream"""
        # This would implement actual WebSocket client
        return []
    
    async def _collect_from_syslog_stream(self, source: Dict[str, Any]) -> List[BaseEvent]:
        """Collect events from syslog stream"""
        # This would implement actual syslog server
        return []
    
    async def _normalize_event(self, raw_event: Dict[str, Any], source: Dict[str, Any]) -> BaseEvent:
        """Normalize raw event data to standard format"""
        try:
            # Extract common fields
            event_id = raw_event.get('id', str(datetime.utcnow().timestamp()))
            timestamp_str = raw_event.get('timestamp', datetime.utcnow().isoformat())
            
            # Parse timestamp
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = datetime.utcnow()
            
            # Determine event type
            event_type = self._determine_event_type(raw_event)
            
            # Create appropriate event object
            if event_type == EventType.AUTHENTICATION:
                return AuthenticationEvent(
                    event_id=event_id,
                    timestamp=timestamp,
                    user_id=raw_event.get('user_id', ''),
                    username=raw_event.get('username', ''),
                    authentication_method=raw_event.get('auth_method', 'unknown'),
                    result=raw_event.get('result', 'unknown'),
                    source_ip=raw_event.get('source_ip'),
                    device_id=raw_event.get('device_id'),
                    mfa_used=raw_event.get('mfa_used', False),
                    raw_data=raw_event
                )
            elif event_type == EventType.DATA_ACCESS:
                return DataAccessEvent(
                    event_id=event_id,
                    timestamp=timestamp,
                    user_id=raw_event.get('user_id', ''),
                    resource_id=raw_event.get('resource_id', ''),
                    resource_type=raw_event.get('resource_type', 'unknown'),
                    action=raw_event.get('action', 'unknown'),
                    result=raw_event.get('result', 'unknown'),
                    source_ip=raw_event.get('source_ip'),
                    data_classification=raw_event.get('data_classification'),
                    bytes_accessed=raw_event.get('bytes_accessed'),
                    raw_data=raw_event
                )
            elif event_type == EventType.NETWORK_ACCESS:
                return NetworkAccessEvent(
                    event_id=event_id,
                    timestamp=timestamp,
                    user_id=raw_event.get('user_id'),
                    device_id=raw_event.get('device_id'),
                    destination_ip=raw_event.get('destination_ip', ''),
                    destination_port=raw_event.get('destination_port', 0),
                    protocol=raw_event.get('protocol', 'unknown'),
                    result=raw_event.get('result', 'unknown'),
                    source_ip=raw_event.get('source_ip'),
                    bytes_sent=raw_event.get('bytes_sent'),
                    bytes_received=raw_event.get('bytes_received'),
                    raw_data=raw_event
                )
            else:
                # Generic base event
                return BaseEvent(
                    event_id=event_id,
                    event_type=event_type,
                    timestamp=timestamp,
                    source_ip=raw_event.get('source_ip'),
                    raw_data=raw_event
                )
                
        except Exception as e:
            logger.error(f"Error normalizing event: {e}")
            # Return basic event on error
            return BaseEvent(
                event_id=str(datetime.utcnow().timestamp()),
                event_type=EventType.SYSTEM_EVENT,
                timestamp=datetime.utcnow(),
                raw_data=raw_event
            )
    
    def _determine_event_type(self, raw_event: Dict[str, Any]) -> EventType:
        """Determine event type from raw event data"""
        # Simple heuristics to determine event type
        if 'login' in str(raw_event).lower() or 'auth' in str(raw_event).lower():
            return EventType.AUTHENTICATION
        elif 'file' in str(raw_event).lower() or 'data' in str(raw_event).lower():
            return EventType.DATA_ACCESS
        elif 'network' in str(raw_event).lower() or 'connection' in str(raw_event).lower():
            return EventType.NETWORK_ACCESS
        else:
            return EventType.SYSTEM_EVENT
    
    async def _deduplicate_events(self, events: List[BaseEvent]) -> List[BaseEvent]:
        """Remove duplicate events"""
        seen_events = set()
        unique_events = []
        
        for event in events:
            # Create a unique key for the event
            event_key = f"{event.event_id}_{event.timestamp}_{event.event_type}"
            
            if event_key not in seen_events:
                seen_events.add(event_key)
                unique_events.append(event)
        
        removed_count = len(events) - len(unique_events)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate events")
        
        return unique_events
    
    def _event_involves_entity(self, event: BaseEvent, entity_id: str) -> bool:
        """Check if event involves a specific entity"""
        # Check various fields that might contain entity references
        if hasattr(event, 'user_id') and event.user_id == entity_id:
            return True
        if hasattr(event, 'device_id') and event.device_id == entity_id:
            return True
        if hasattr(event, 'source_ip') and event.source_ip == entity_id:
            return True
        
        # Check raw data for entity references
        if event.raw_data:
            raw_str = str(event.raw_data).lower()
            if entity_id.lower() in raw_str:
                return True
        
        return False
    
    def _event_involves_entities(self, event: BaseEvent, entity_ids: List[str]) -> bool:
        """Check if event involves any of the specified entities"""
        return any(self._event_involves_entity(event, entity_id) for entity_id in entity_ids)
    
    def _generate_mock_events(
        self,
        start_time: datetime,
        end_time: datetime,
        entity_ids: Optional[List[str]],
        count: int
    ) -> List[BaseEvent]:
        """Generate mock events for testing"""
        mock_events = []
        
        if not entity_ids:
            entity_ids = ['user_001', 'user_002', 'device_001']
        
        for i in range(count):
            # Random timestamp within range
            time_diff = end_time - start_time
            random_offset = time_diff.total_seconds() * (i / count)
            event_time = start_time + timedelta(seconds=random_offset)
            
            # Random entity
            entity_id = entity_ids[i % len(entity_ids)]
            
            # Create mock authentication event
            event = AuthenticationEvent(
                event_id=f"mock_event_{i}",
                timestamp=event_time,
                user_id=entity_id,
                username=f"user_{entity_id}",
                authentication_method="password",
                result="success",
                source_ip="192.168.1.100",
                mfa_used=i % 2 == 0,
                raw_data={"mock": True, "index": i}
            )
            
            mock_events.append(event)
        
        return mock_events 