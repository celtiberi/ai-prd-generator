import pytest
import logging
from typing import List, Dict, Any, Optional
from pubsub import pub

class BaseAgentTest:
    """Base class for agent tests providing common testing functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_test(self):
        """Setup test state before each test method"""
        self.events_received: List[Dict[str, Any]] = []
        self._subscribed_topics: List[str] = []
        self.logger = logging.getLogger(__name__)
        yield
        # Cleanup after test
        self.cleanup_subscriptions()
    
    def track_event(self, event: Dict[str, Any]) -> None:
        """Track events and log them for debugging."""
        self.logger.debug(f"Received event: {event}")
        self.events_received.append(event)
    
    def subscribe_to_events(self, topics: List[str]) -> None:
        """Subscribe to multiple event topics."""
        for topic in topics:
            self.logger.debug(f"Subscribing to topic: {topic}")
            # Create a stable reference to the callback
            callback = lambda event, topic=topic: self.track_event(event)
            pub.subscribe(callback, topic)
            self._subscribed_topics.append((topic, callback))
    
    def cleanup_subscriptions(self) -> None:
        """Clean up all event subscriptions."""
        for topic, callback in self._subscribed_topics:
            self.logger.debug(f"Unsubscribing from topic: {topic}")
            pub.unsubscribe(callback, topic)
        self._subscribed_topics.clear()
        self.events_received.clear()
    
    def assert_event_received(self, event_type: str, message: Optional[str] = None) -> tuple[bool, str]:
        """Assert that an event of a specific type was received."""
        msg = message or f"Should receive {event_type} event"
        received = False
        for event in self.events_received:
            if isinstance(event, dict) and event.get("type") == event_type:
                received = True
                break
            elif isinstance(event, str) and event == event_type:
                received = True
                break
        return received, msg 
    
    @staticmethod
    def is_quota_exceeded(error_response: Dict) -> bool:
        """Check if error is due to exceeded quota"""
        if not error_response or 'error' not in error_response:
            return False
        
        error = error_response.get('error', {})
        return (
            error.get('code') == 'insufficient_quota' or
            error.get('type') == 'insufficient_quota'
        ) 