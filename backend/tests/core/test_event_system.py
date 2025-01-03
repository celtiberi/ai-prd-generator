import pytest
from datetime import datetime
from unittest.mock import Mock
import time
from backend.core.event_system import EventSystem, EventMessage

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
    mock_handler = Mock()
    event_system.subscribe("test_event", mock_handler, "test_agent")
    
    event_system.publish(
        event_type="test_event",
        source_agent="source",
        target_agent="test_agent",
        payload={"test": "data"},
        correlation_id="test_123"
    )
    
    # Give pubsub time to process
    time.sleep(0.1)
    mock_handler.assert_called_once()
    event = mock_handler.call_args[0][0]
    assert event.type == "test_event"
    assert event.payload == {"test": "data"}

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
    mock_error_handler = Mock()
    event_system.subscribe("error_occurred", mock_error_handler)
    
    def failing_handler(event):
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
    mock_error_handler.assert_called_once()
    error_event = mock_error_handler.call_args[0][0]
    assert error_event.type == "handler_error"
    assert "Test handler error" in str(error_event.payload["error"]) 