import pytest
from unittest.mock import Mock
from ...agents.lead_agent import LeadAgent, ProjectContext

def test_lead_agent_initialization(event_bus):
    """Test lead agent initialization"""
    agent = LeadAgent(event_bus)
    assert agent.name == "LeadAgent"
    assert agent.project_context is None
    assert isinstance(agent.active_tasks, dict)

def test_project_initialization(event_bus, sample_project_data):
    """Test project initialization"""
    agent = LeadAgent(event_bus)
    result = agent.initialize_project(sample_project_data)
    
    assert result["status"] == "initialized"
    assert isinstance(agent.project_context, ProjectContext)
    assert agent.project_context.title == sample_project_data["title"]
    assert agent.project_context.objectives == sample_project_data["objectives"]

def test_research_phase_start(event_bus, sample_project_data):
    """Test research phase initialization"""
    agent = LeadAgent(event_bus)
    
    # Track published events
    published_events = []
    def track_event(event):
        if event.type == "research_request":
            published_events.append(event)
    
    event_bus.subscribe("research_request", track_event)
    
    # Initialize project
    agent.initialize_project(sample_project_data)
    
    # Wait for event processing
    import time
    time.sleep(0.1)
    
    # Verify research tasks were created
    assert len(published_events) > 0
    for event in published_events:
        assert "query" in event.data
        assert "context" in event.data
        assert "task_id" in event.data

def test_handle_research_complete(event_bus, sample_project_data, mock_research_results):
    """Test handling of completed research"""
    agent = LeadAgent(event_bus)
    agent.initialize_project(sample_project_data)
    
    # Track memory updates
    memory_updates = []
    def track_memory_update(event):
        if event.type == "update_memory":
            memory_updates.append(event)
    
    event_bus.subscribe("update_memory", track_memory_update)
    
    # Simulate research completion
    agent._handle_research_complete(mock_research_results)
    
    # Wait for event processing
    import time
    time.sleep(0.1)
    
    # Verify memory was updated
    assert len(memory_updates) > 0
    assert memory_updates[0].data["type"] == "research"

def test_feature_definition_phase(event_bus, sample_project_data):
    """Test transition to feature definition phase"""
    agent = LeadAgent(event_bus)
    agent.initialize_project(sample_project_data)
    
    # Track feature requests
    feature_requests = []
    def track_feature_request(event):
        if event.type == "feature_request":
            feature_requests.append(event)
    
    event_bus.subscribe("feature_request", track_feature_request)
    
    # Simulate research phase completion
    agent.project_context.status = "research_complete"
    agent._start_feature_definition()
    
    # Wait for event processing
    import time
    time.sleep(0.1)
    
    # Verify feature definition was initiated
    assert len(feature_requests) > 0
    assert "context" in feature_requests[0].data

def test_handle_user_feedback(event_bus, sample_project_data):
    """Test handling of user feedback"""
    agent = LeadAgent(event_bus)
    agent.initialize_project(sample_project_data)
    
    feedback_data = {
        "features": [
            {
                "name": "Authentication",
                "feedback": "Add support for SSO"
            }
        ],
        "objectives": ["Add performance monitoring"]
    }
    
    # Track feature requests resulting from feedback
    feature_requests = []
    def track_feature_request(event):
        if event.type == "feature_request":
            feature_requests.append(event)
    
    event_bus.subscribe("feature_request", track_feature_request)
    
    # Submit feedback
    agent._handle_user_feedback(feedback_data)
    
    # Wait for event processing
    import time
    time.sleep(0.1)
    
    # Verify feedback was processed
    assert agent.project_context.status == "updating"
    assert len(feature_requests) > 0 