from typing import Dict, Any, Optional, List, Set, Callable, Type
import random
import time
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from pubsub import pub
from pubsub.core.listener import IListenerExcHandler
import uuid
import json
from collections import deque

@dataclass
class EventMessage:
    """Event message structure as defined in schemas.md"""
    type: str
    source_agent: str
    target_agent: str
    timestamp: datetime
    payload: Any
    correlation_id: str

@dataclass
class StoredEvent:
    """Event storage structure"""
    topic: str
    data: Any
    timestamp: datetime
    processing_time_ms: float

class EventStore:
    """Simple in-memory event store with size limit"""
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.events: deque = deque(maxlen=max_size)
        self.start_time = time.time()
    
    def store_event(self, topic: str, data: Any):
        """Store an event with processing time"""
        processing_time_ms = (time.time() - self.start_time) * 1000  # Convert to ms
        self.start_time = time.time()  # Reset for next event
        
        event = StoredEvent(
            topic=topic,
            data=data,
            timestamp=datetime.utcnow(),
            processing_time_ms=processing_time_ms
        )
        self.events.append(event)
    
    def get_events(self) -> List[StoredEvent]:
        """Get all stored events"""
        return list(self.events)
    
    def clear(self):
        """Clear all stored events"""
        self.events.clear()

class EventSystem:
    """Event system implementation using pypubsub"""
    
    VALID_EVENT_TYPES = {
        "system": {
            "state_changes": [
                "initialized",
                "shutdown",
                "error"
            ],
            "monitoring": [
                "heartbeat",
                "performance_metric"
            ]
        },
        "agent": {
            "events": [
                "test_event",
                "test"
            ]
        }
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._retry_counts: Dict[str, int] = {}
        self._subscriptions: Dict[str, Set[tuple]] = {}
        
        # Add error handler for listener exceptions
        self._exc_handler = EventSystemExcHandler(self)
        pub.setListenerExcHandler(self._exc_handler)
        
        # Setup event store
        self._event_store = EventStore()
        
        # Track event processing
        self._event_handler = self._create_event_handler()
        pub.subscribe(self._event_handler, pub.ALL_TOPICS)
    
    def _validate_event_payload(self, event_type: str, payload: Any) -> bool:
        """Validate event payload against expected schema"""
        if event_type.startswith("system.error"):
            required_fields = {"error", "message", "correlation_id"}
            return isinstance(payload, dict) and all(field in payload for field in required_fields)
        
        if event_type.startswith("agent."):
            return isinstance(payload, dict)
        
        return True  # Other events don't have schema requirements
    
    def _add_jitter(self, delay: float) -> float:
        """Add random jitter to retry delay"""
        return delay * (1 + random.random() * 0.1)
    
    def subscribe(
        self,
        event_type: str,
        handler: Callable,
        agent_id: Optional[str] = None,
        filter_fn: Optional[Callable] = None
    ) -> None:
        """Subscribe to events with filtering support"""
        try:
            # Don't format system events with agent prefix
            if event_type.startswith("system."):
                topic = event_type
            elif event_type == "*":
                topic = "system"
            elif agent_id:
                topic = self._format_topic(
                    "agent.{agent}.{event}",
                    agent=agent_id,
                    event=event_type
                )
            else:
                topic = event_type
                
            if not self._validate_event_type(topic):
                raise ValueError(f"Invalid event type: {topic}")
            
            # Create a wrapper handler that applies the filter
            if filter_fn:
                def filtered_handler(data=None, **kwargs):
                    if data is not None and filter_fn(data):
                        handler(data)
                actual_handler = filtered_handler
            else:
                actual_handler = handler
            
            pub.subscribe(actual_handler, topic)
            
            # Track subscription with the actual handler we subscribed
            if agent_id not in self._subscriptions:
                self._subscriptions[agent_id] = set()
            self._subscriptions[agent_id].add((topic, actual_handler))
            
            self.logger.debug(f"Successfully subscribed to {topic}")
            
        except Exception as e:
            self.logger.error(f"Error subscribing to event: {e}", exc_info=True)
            raise
    
    def unsubscribe_all(self, agent_id: str) -> None:
        """Unsubscribe from all topics for an agent"""
        if agent_id in self._subscriptions:
            for topic, handler in self._subscriptions[agent_id]:
                pub.unsubscribe(listener=handler, topicName=topic)  # Fix unsubscribe call
            del self._subscriptions[agent_id]
            self.logger.debug(f"Unsubscribed {agent_id} from all topics")

    def _create_event_message(
        self, 
        event_type: str,
        source_agent: str,
        target_agent: str,
        payload: Any,
        correlation_id: str
    ) -> EventMessage:
        """Create a properly formatted event message"""
        return EventMessage(
            type=event_type,
            source_agent=source_agent,
            target_agent=target_agent,
            timestamp=datetime.utcnow(),
            payload=payload,
            correlation_id=correlation_id
        )

    def _format_topic(self, pattern: str, **kwargs) -> str:
        """Format topic string based on subscription patterns"""
        try:
            return pattern.format(**kwargs)
        except KeyError as e:
            self.logger.error(f"Invalid topic format: {e}")
            raise ValueError(f"Missing required topic parameter: {e}")

    def publish(
        self,
        event_type: str,
        source_agent: str,
        target_agent: str,
        payload: Any,
        correlation_id: str,
        retry: bool = True
    ) -> None:
        """Publish an event with retry logic"""
        event = self._create_event_message(
            event_type=event_type,
            source_agent=source_agent,
            target_agent=target_agent,
            payload=payload,
            correlation_id=correlation_id
        )
        
        try:
            if event_type.startswith("system."):  # Don't format system events
                topic = event_type
            elif event_type == "*":
                topic = "system"
            elif target_agent != "*":
                topic = self._format_topic(
                    "agent.{agent}.{event}",
                    agent=target_agent,
                    event=event_type
                )
            else:
                topic = event_type
            
            self.logger.debug(f"Publishing to topic {topic} with payload: {payload}")
            pub.sendMessage(topic, data=event.payload)
            self.logger.debug(f"Successfully published event: {event_type} to {topic}")
            
        except Exception as e:
            self.logger.error(f"Error publishing event: {e}", exc_info=True)
            if retry:
                self._handle_publish_error(event)

    def _handle_publish_error(self, event: EventMessage) -> None:
        """Implement retry with backoff and jitter"""
        event_key = f"{event.correlation_id}:{event.type}"
        retry_count = self._retry_counts.get(event_key, 0)
        
        if retry_count < 3:
            base_delay = min(30.0, (2 ** retry_count))
            delay = self._add_jitter(base_delay)
            time.sleep(delay)
            self._retry_counts[event_key] = retry_count + 1
            self.publish(
                event_type=event.type,
                source_agent=event.source_agent,
                target_agent=event.target_agent,
                payload=event.payload,
                correlation_id=event.correlation_id,
                retry=True
            )
        else:
            self.logger.error(f"Max retries reached for event: {event}")
            self.publish(
                event_type="system.error",
                source_agent=event.source_agent,
                target_agent="system_monitor",
                payload={
                    "error": "max_retries_exceeded",
                    "original_event": event
                },
                correlation_id=event.correlation_id,
                retry=False
            ) 

    def get_event_history(
        self,
        topic_filter: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict]:
        """Get filtered event history"""
        events = self._event_store.get_events()
        
        if topic_filter:
            events = [e for e in events if e.topic.startswith(topic_filter)]
            
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
            
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
            
        return [asdict(e) for e in events]
    
    def clear_event_history(self):
        """Clear event history"""
        self._event_store.clear()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get event system metrics"""
        events = self._event_store.get_events()
        return {
            "total_events": len(events),
            "avg_processing_time": sum(e.processing_time_ms for e in events) / len(events) if events else 0,
            "events_by_topic": self._count_events_by_topic(events),
            "active_subscriptions": self._count_active_subscriptions()
        }
    
    def _count_events_by_topic(self, events: List[StoredEvent]) -> Dict[str, int]:
        """Count events by topic"""
        counts = {}
        for event in events:
            topic = event.topic
            counts[topic] = counts.get(topic, 0) + 1
        return counts
    
    def _count_active_subscriptions(self) -> Dict[str, int]:
        """Count active subscriptions by agent"""
        return {
            agent_id: len(subs)
            for agent_id, subs in self._subscriptions.items()
        } 

    def _create_event_handler(self):
        """Create event tracking handler"""
        def handler(topic=pub.AUTO_TOPIC, **kwargs):
            self._event_store.store_event(topic.getName(), kwargs.get('data'))
        return handler 

    def _validate_event_type(self, event_type: str) -> bool:
        """Validate event type against schema"""
        parts = event_type.split(".")
        
        # Handle special cases
        if event_type == "*":
            return True
        
        # Handle agent events
        if parts[0] == "agent" and len(parts) == 3:
            category = parts[0]
            event = parts[2]
            return event in self.VALID_EVENT_TYPES[category]["events"]
            
        # Handle system events
        if parts[0] == "system" and len(parts) == 2:
            category = parts[0]
            event = parts[1]
            for subcategory in self.VALID_EVENT_TYPES[category].values():
                if event in subcategory:
                    return True
        
        return False

class EventSystemExcHandler(pub.IListenerExcHandler):
    """Exception handler for event system"""
    def __init__(self, event_system):
        self.event_system = event_system
        
    def __call__(self, listener_id, topic_obj):
        """Called when a listener raises an exception"""
        self.event_system.logger.debug(
            f"Exception handler called for listener {listener_id} on topic {topic_obj.getName()}"
        )
        self.event_system.publish(
            event_type="system.error",
            source_agent="system",
            target_agent="system_monitor",
            payload={
                "error": "listener_error",
                "listener": listener_id,
                "topic": topic_obj.getName()
            },
            correlation_id=str(uuid.uuid4()),
            retry=False
        ) 