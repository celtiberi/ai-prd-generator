import pytest
from datetime import datetime
from unittest.mock import Mock
import time
from backend.core.event_system import EventSystem, EventMessage
from unittest.mock import patch

@pytest.fixture
def event_system():
    return EventSystem()

def test_event_message_creation(event_system):
    """Test event message creation with required fields"""
    event = event_system._create_event_message(
        event_type="test_event",
        source_agent="test_source",
        target_agent="test_target",
        payload={"test": "data"},
        correlation_id="test_123"
    )
    
    assert isinstance(event, EventMessage)
    assert event.type == "test_event"
    assert event.source_agent == "test_source"
    assert event.target_agent == "test_target"
    assert isinstance(event.timestamp, datetime)
    assert event.payload == {"test": "data"}
    assert event.correlation_id == "test_123"

def test_publish_subscribe(event_system):
    """Test basic publish/subscribe functionality"""
    received_events = []
    
    def test_handler(data=None):
        received_events.append(data)
    
    event_system.subscribe("test_event", test_handler, "test_agent")
    
    event_system.publish(
        event_type="test_event",
        source_agent="source",
        target_agent="test_agent",
        payload={"test": "data"},
        correlation_id="test_123"
    )
    
    time.sleep(0.1)
    assert len(received_events) == 1
    assert received_events[0] == {"test": "data"}

def test_retry_logic(event_system, monkeypatch):
    """Test retry logic with backoff"""
    mock_pub = Mock(side_effect=[Exception("Test error"), None])
    monkeypatch.setattr("pubsub.pub.sendMessage", mock_pub)
    
    event_system.publish(
        event_type="test_event",
        source_agent="source",
        target_agent="test_agent",
        payload={"test": "data"},
        correlation_id="test_123"
    )
    
    assert mock_pub.call_count == 2

def test_error_handling(event_system):
    """Test error event generation"""
    received_errors = []
    
    def error_handler(data=None):
        event_system.logger.debug(f"Error handler received: {data}")
        received_errors.append(data)
    
    event_system.subscribe("system.error", error_handler)
    
    def failing_handler(data=None):
        event_system.logger.debug("Failing handler called, about to raise exception")
        raise Exception("Test handler error")
    
    event_system.subscribe("test_event", failing_handler, "test_agent")
    
    event_system.publish(
        event_type="test_event",
        source_agent="source",
        target_agent="test_agent",
        payload={"test": "data"},
        correlation_id="test_123"
    )
    
    time.sleep(0.1)
    event_system.logger.debug(f"Received errors: {received_errors}")
    assert len(received_errors) == 1
    error = received_errors[0]
    assert error["error"] == "listener_error"
    assert "failing_handler" in error["listener"] 

@pytest.mark.asyncio
async def test_event_validation():
    """Test event type validation"""
    event_system = EventSystem()
    
    # Valid event
    event_system.subscribe("system.initialized", lambda x: None)
    
    # Invalid event
    with pytest.raises(ValueError):
        event_system.subscribe("invalid.event", lambda x: None)

@pytest.mark.asyncio
async def test_subscription_cleanup():
    """Test subscription cleanup"""
    event_system = EventSystem()
    received = []
    
    def handler(data=None):
        received.append(data)
    
    event_system.subscribe("test_event", handler, "test_agent")
    event_system.unsubscribe_all("test_agent")
    
    # Should not receive event after unsubscribe
    event_system.publish(
        event_type="test_event",
        source_agent="source",
        target_agent="test_agent",
        payload={"test": "data"},
        correlation_id="test_123"
    )
    
    assert len(received) == 0

@pytest.mark.asyncio
async def test_retry_with_jitter():
    """Test retry backoff with jitter"""
    event_system = EventSystem()
    delays = []
    
    def track_delay(delay):
        delays.append(delay)
    
    # Mock time.sleep to track delays
    with patch('time.sleep', side_effect=track_delay):
        event_system._handle_publish_error(
            EventMessage(
                type="test",
                source_agent="test",
                target_agent="test",
                timestamp=datetime.now(),
                payload={},
                correlation_id="test"
            )
        )
    
    # Verify delays increase with jitter
    assert len(delays) > 0
    for i in range(1, len(delays)):
        assert delays[i] > delays[i-1] 

@pytest.mark.asyncio
async def test_event_history():
    """Test event history storage and retrieval"""
    event_system = EventSystem()
    
    # Create test events
    event_system.publish(
        event_type="test_event",
        source_agent="test",
        target_agent="test",
        payload={"test": "data"},
        correlation_id="test_123"
    )
    
    time.sleep(0.1)  # Allow event processing
    
    history = event_system.get_event_history()
    assert len(history) == 1
    assert history[0]["topic"] == "agent.test.test_event"
    assert "processing_time_ms" in history[0]

@pytest.mark.asyncio
async def test_event_filtering():
    """Test event subscription filtering"""
    event_system = EventSystem()
    received = []
    
    def filter_fn(data):
        return data.get("important") == True
    
    def handler(data=None):
        received.append(data)
    
    event_system.subscribe(
        "test_event",
        handler,
        "test_agent",
        filter_fn=filter_fn
    )
    
    # Should be filtered out
    event_system.publish(
        event_type="test_event",
        source_agent="source",
        target_agent="test_agent",
        payload={"important": False},
        correlation_id="test_1"
    )
    
    # Should pass filter
    event_system.publish(
        event_type="test_event",
        source_agent="source",
        target_agent="test_agent",
        payload={"important": True},
        correlation_id="test_2"
    )
    
    time.sleep(0.1)
    assert len(received) == 1
    assert received[0]["important"] == True

@pytest.mark.asyncio
async def test_event_metrics():
    """Test event metrics collection"""
    event_system = EventSystem()
    
    # Generate some test events
    for i in range(3):
        event_system.publish(
            event_type="test_event",
            source_agent="test",
            target_agent="test",
            payload={"test": i},
            correlation_id=f"test_{i}"
        )
    
    time.sleep(0.1)
    
    metrics = event_system.get_metrics()
    assert metrics["total_events"] == 3
    assert metrics["avg_processing_time"] > 0
    assert "agent.test.test_event" in metrics["events_by_topic"]
    assert metrics["events_by_topic"]["agent.test.test_event"] == 3 