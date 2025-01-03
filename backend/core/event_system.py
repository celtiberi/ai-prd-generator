from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
from pubsub import pub
import json
from functools import wraps
import time

@dataclass
class EventMessage:
    """Event message structure as defined in schemas.md"""
    type: str
    source_agent: str
    target_agent: str
    timestamp: datetime
    payload: Any
    correlation_id: str

class EventSystem:
    """Event system implementation using pypubsub"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Store retry counts for error handling
        self._retry_counts: Dict[str, int] = {}
        
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
            # Format topic based on patterns from events.md
            if target_agent != "*":
                topic = self._format_topic(
                    "agent.{target}.{event}",
                    target=target_agent,
                    event=event_type
                )
            else:
                topic = self._format_topic(
                    "system.{event}",
                    event=event_type
                )
            
            pub.sendMessage(topic, event=event)
            self.logger.debug(f"Published event: {event_type} to {topic}")
            
        except Exception as e:
            self.logger.error(f"Error publishing event: {e}")
            if retry:
                self._handle_publish_error(event)

    def _handle_publish_error(self, event: EventMessage) -> None:
        """Implement retry with backoff as specified in events.md"""
        event_key = f"{event.correlation_id}:{event.type}"
        retry_count = self._retry_counts.get(event_key, 0)
        
        if retry_count < 3:  # Max retries from events.md
            delay = min(30.0, (2 ** retry_count) + (time.random() * 0.1))  # With jitter
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
            # Publish error event
            self.publish(
                event_type="error_occurred",
                source_agent=event.source_agent,
                target_agent="system_monitor",
                payload={
                    "error": "max_retries_exceeded",
                    "original_event": event
                },
                correlation_id=event.correlation_id,
                retry=False
            )

    def subscribe(
        self,
        event_type: str,
        handler: Callable,
        agent_id: Optional[str] = None
    ) -> None:
        """Subscribe to events with proper topic formatting"""
        try:
            if agent_id:
                topic = self._format_topic(
                    "agent.{agent}.{event}",
                    agent=agent_id,
                    event=event_type
                )
            else:
                topic = self._format_topic(
                    "system.{event}",
                    event=event_type
                )
            
            @wraps(handler)
            def wrapped_handler(event: EventMessage):
                try:
                    handler(event)
                except Exception as e:
                    self.logger.error(f"Error in event handler: {e}")
                    # Publish error event
                    self.publish(
                        event_type="handler_error",
                        source_agent=event.target_agent,
                        target_agent="system_monitor",
                        payload={
                            "error": str(e),
                            "handler": handler.__name__,
                            "event": event
                        },
                        correlation_id=event.correlation_id,
                        retry=False
                    )
            
            pub.subscribe(wrapped_handler, topic)
            self.logger.debug(f"Subscribed to {topic}")
            
        except Exception as e:
            self.logger.error(f"Error subscribing to event: {e}")
            raise

    def unsubscribe(
        self,
        event_type: str,
        handler: Callable,
        agent_id: Optional[str] = None
    ) -> None:
        """Unsubscribe from events"""
        try:
            if agent_id:
                topic = self._format_topic(
                    "agent.{agent}.{event}",
                    agent=agent_id,
                    event=event_type
                )
            else:
                topic = self._format_topic(
                    "system.{event}",
                    event=event_type
                )
            
            pub.unsubscribe(handler, topic)
            self.logger.debug(f"Unsubscribed from {topic}")
            
        except Exception as e:
            self.logger.error(f"Error unsubscribing from event: {e}")
            raise 