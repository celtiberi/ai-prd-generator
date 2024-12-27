import pytest
from ...agents.base_agent import BaseAgent
from ...events.event_bus import Event

class TestAgent(BaseAgent):
    """Test implementation of BaseAgent"""
    def __init__(self, name, event_bus):
        super().__init__(name, event_bus)
        self.handled_events = []

    def handle_event(self, event):
        self.handled_events.append(event)

    def execute_task(self, task):
        return f"Executed {task}"

def test_base_agent_initialization(event_bus):
    """Test agent initialization"""
    agent = TestAgent("test_agent", event_bus)
    assert agent.name == "test_agent"
    assert agent.event_bus == event_bus

def test_base_agent_event_handling(event_bus):
    """Test event subscription and handling"""
    agent = TestAgent("test_agent", event_bus)
    agent.subscribe("test_event")
    
    # Publish test event
    event_data = {"message": "test"}
    event_bus.publish("test_event", event_data)
    
    # Wait for event processing
    import time
    time.sleep(0.1)
    
    assert len(agent.handled_events) == 1
    assert agent.handled_events[0].type == "test_event"
    assert agent.handled_events[0].data == event_data

def test_base_agent_publishing(event_bus):
    """Test event publishing"""
    agent = TestAgent("test_agent", event_bus)
    received_events = []
    
    def test_callback(event):
        received_events.append(event)
    
    event_bus.subscribe("test_event", test_callback)
    agent.publish("test_event", {"message": "test"})
    
    # Wait for event processing
    import time
    time.sleep(0.1)
    
    assert len(received_events) == 1
    assert received_events[0].type == "test_event"
    assert received_events[0].data["message"] == "test" 