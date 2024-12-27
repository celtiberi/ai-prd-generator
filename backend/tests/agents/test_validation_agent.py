import pytest
from ...agents.validation_agent import ValidationAgent

@pytest.fixture
def sample_feature():
    return {
        "name": "User Authentication",
        "description": "Implement secure user authentication system",
        "requirements": [
            "Support OAuth 2.0 authentication",
            "Implement MFA",
            "Password hashing with bcrypt"
        ],
        "dependencies": ["Database", "Email Service"],
        "priority": "high",
        "status": "draft"
    }

def test_validation_agent_initialization(event_bus):
    """Test validation agent initialization"""
    agent = ValidationAgent(event_bus)
    assert agent.name == "ValidationAgent"
    assert len(agent.validation_rules) > 0

def test_completeness_validation(event_bus, sample_feature):
    """Test feature completeness validation"""
    agent = ValidationAgent(event_bus)
    result = agent._check_completeness(sample_feature)
    assert isinstance(result, dict)
    assert "score" in result
    assert "feedback" in result
    assert result["score"] >= 0.0 and result["score"] <= 1.0

def test_consistency_validation(event_bus, sample_feature):
    """Test feature consistency validation"""
    agent = ValidationAgent(event_bus)
    result = agent._check_consistency(sample_feature)
    assert isinstance(result, dict)
    assert result["score"] >= 0.0
    assert "requirements_consistent" in result["details"]

def test_feasibility_validation(event_bus, sample_feature):
    """Test feature feasibility validation"""
    agent = ValidationAgent(event_bus)
    result = agent._check_feasibility(sample_feature)
    assert isinstance(result, dict)
    assert "dependencies_feasible" in result["details"]
    assert "technical_complexity" in result["details"]

def test_validation_feedback_generation(event_bus, sample_feature):
    """Test feedback generation from validation results"""
    agent = ValidationAgent(event_bus)
    validation_results = [
        {
            "rule": "completeness",
            "score": 0.6,
            "feedback": "Missing detailed requirements"
        },
        {
            "rule": "consistency",
            "score": 0.8,
            "feedback": "Requirements align with description"
        }
    ]
    feedback = agent._generate_feedback(validation_results)
    assert isinstance(feedback, str)
    assert "Completeness" in feedback

def test_full_validation_process(event_bus, sample_feature):
    """Test complete validation process"""
    agent = ValidationAgent(event_bus)
    
    # Track validation results
    validation_results = []
    def track_validation(event):
        if event.type == "validation_complete":
            validation_results.append(event.data)
    
    event_bus.subscribe("validation_complete", track_validation)
    
    # Trigger validation
    agent.handle_event({
        "type": "validation_request",
        "data": {"feature": sample_feature}
    })
    
    # Wait for event processing
    import time
    time.sleep(0.1)
    
    # Verify validation results
    assert len(validation_results) > 0
    assert "validation_results" in validation_results[0]
    assert "feedback" in validation_results[0] 