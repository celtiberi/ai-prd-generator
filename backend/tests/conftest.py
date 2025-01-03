import pytest
import os
from typing import Dict, Any
from ..agents.memory_agent import MemoryAgent
from ..agents.lead_agent import LeadAgent
from ..agents.research_agent import ResearchAgent
from ..agents.feature_agent import FeatureAgent
from ..agents.validation_agent import ValidationAgent
from pubsub import pub
from config.settings import Settings  # Import Settings
import logging

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables"""
    settings = Settings()  # This will load .env automatically
    os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY  # Ensure it's in os.environ
    yield

@pytest.fixture
def test_settings():
    """Real settings instance for testing"""
    settings = Settings()
    settings.OPENAI_MODEL = settings.TEST_MODEL  # Use cheaper model for tests
    return settings

@pytest.fixture
def sample_project_data():
    """Sample project data for testing"""
    return {
        "title": "Test Project",
        "description": "A test project for unit testing",
        "objectives": [
            "Implement user authentication",
            "Create data visualization dashboard",
            "Set up automated testing"
        ]
    }

@pytest.fixture
def mock_research_results():
    """Mock research results"""
    return {
        "task_id": "research_1",
        "query": "user authentication best practices",
        "results": {
            "main_findings": [
                "Use OAuth 2.0 for authentication",
                "Implement MFA for security",
                "Store passwords using bcrypt"
            ],
            "sources": [
                {
                    "title": "Auth Best Practices",
                    "url": "https://example.com/auth",
                    "snippet": "OAuth 2.0 is recommended..."
                }
            ]
        }
    }

@pytest.fixture
def agent_system(test_settings):
    """Create a complete agent system for integration tests"""
    agents = {
        "memory": MemoryAgent(test_settings),
        "lead": LeadAgent(settings=test_settings),
        "research": ResearchAgent(test_settings.TAVILY_API_KEY),
        "feature": FeatureAgent(),
        "validation": ValidationAgent()
    }
    return agents 

@pytest.fixture(autouse=True)
def clean_pubsub():
    """Clean up pubsub after each test"""
    yield
    pub.unsubAll() 

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers",
        "integration: mark test as an integration test"
    ) 

@pytest.fixture(autouse=True)
def setup_logging():
    """Set up logging for all tests"""
    logging.basicConfig(level=logging.DEBUG) 

@pytest.fixture
def sample_feature_request():
    """Sample feature request for testing"""
    return {
        "feature": {
            "name": "Game Board",
            "description": "Interactive game board component"
        },
        "context": {
            "project_type": "game",
            "tech_stack": ["React", "TypeScript"]
        }
    }

@pytest.fixture
def sample_project_summary():
    """Sample project summary for testing"""
    return {
        "title": "Tic Tac Toe Game",
        "description": "Interactive game for learning React",
        "goals": ["Learn state management", "Practice React components"],
        "key_features": ["Game board", "Move history", "Win detection"]
    }

@pytest.fixture
def sample_feature():
    """Sample feature for testing"""
    return {
        "name": "Authentication",
        "description": "User authentication system",
        "requirements": ["OAuth 2.0", "MFA support"],
        "priority": "high",
        "dependencies": []
    }

@pytest.fixture
def sample_context():
    """Sample context for testing"""
    return {
        "project_type": "web_app",
        "security_requirements": "high",
        "user_base": "external"
    } 