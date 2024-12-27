import pytest
from typing import Dict, Any
from ..events.event_bus import EventBus
from ..agents.memory_agent import MemoryAgent
from ..agents.lead_agent import LeadAgent
from ..agents.research_agent import ResearchAgent
from ..agents.feature_agent import FeatureAgent
from ..agents.validation_agent import ValidationAgent

@pytest.fixture
def event_bus():
    """Create a fresh event bus for each test"""
    return EventBus()

@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    class MockSettings:
        TAVILY_API_KEY = "test_key"
        OPENAI_API_KEY = "test_key"
        VECTOR_DIM = 768
        SQLITE_DB_PATH = ":memory:"  # Use in-memory SQLite for tests
        FAISS_INDEX_PATH = "test_index"
    return MockSettings()

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
def agent_system(event_bus, mock_settings):
    """Create a complete agent system for integration tests"""
    agents = {
        "memory": MemoryAgent(event_bus, mock_settings),
        "lead": LeadAgent(event_bus),
        "research": ResearchAgent(event_bus, mock_settings.TAVILY_API_KEY),
        "feature": FeatureAgent(event_bus),
        "validation": ValidationAgent(event_bus)
    }
    return agents 