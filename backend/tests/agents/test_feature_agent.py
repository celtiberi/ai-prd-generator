import pytest
from ...agents.feature_agent import FeatureAgent, Feature

def test_feature_agent_initialization(event_bus):
    """Test feature agent initialization"""
    agent = FeatureAgent(event_bus)
    assert agent.name == "FeatureAgent"
    assert agent.current_context is None
    assert isinstance(agent.research_data, dict)

def test_feature_creation_from_objective(event_bus, mock_research_results):
    """Test feature creation from objective"""
    agent = FeatureAgent(event_bus)
    agent._update_research_data(mock_research_results)
    
    objective = "Implement user authentication with OAuth2"
    feature = agent._create_feature_from_objective(objective)
    
    assert isinstance(feature, Feature)
    assert feature.name is not None
    assert feature.description == objective
    assert len(feature.requirements) > 0
    assert feature.status == "draft"

def test_requirements_extraction(event_bus, mock_research_results):
    """Test requirement extraction from research data"""
    agent = FeatureAgent(event_bus)
    agent._update_research_data(mock_research_results)
    
    objective = "Implement user authentication"
    requirements = agent._extract_requirements(objective)
    
    assert len(requirements) > 0
    assert any("OAuth" in req for req in requirements)

def test_feature_refinement(event_bus):
    """Test feature refinement based on feedback"""
    agent = FeatureAgent(event_bus)
    
    feedback = {
        "feature": {
            "name": "Authentication",
            "description": "User authentication system",
            "requirements": ["OAuth 2.0", "MFA"],
            "dependencies": [],
            "priority": "high",
            "status": "draft"
        },
        "feedback": "Add password policies"
    }
    
    # Track validation requests
    validation_requests = []
    def track_validation(event):
        if event.type == "feature_defined":
            validation_requests.append(event)
    
    event_bus.subscribe("feature_defined", track_validation)
    
    # Refine feature
    agent._refine_features(feedback)
    
    # Wait for event processing
    import time
    time.sleep(0.1)
    
    # Verify refinement
    assert len(validation_requests) > 0
    refined_feature = validation_requests[0].data["feature"]
    assert refined_feature["status"] == "refined"

def test_research_data_update(event_bus, mock_research_results):
    """Test research data update handling"""
    agent = FeatureAgent(event_bus)
    
    update_event = {
        "type": "memory_updated",
        "data": {
            "type": "research",
            "text": '{"findings": "test findings"}',
            "name": "test_research"
        }
    }
    
    agent._update_research_data(update_event)
    assert "test_research" in agent.research_data 