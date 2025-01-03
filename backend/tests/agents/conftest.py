import pytest
from unittest.mock import Mock, AsyncMock
from ...services.llm_service import LLMService
from tavily import TavilyClient

@pytest.fixture
def mock_llm_service():
    """Mock LLM service for unit testing"""
    mock = Mock(spec=LLMService)
    mock.structured_output = AsyncMock()
    mock.structured_output.return_value = {
        "status": "success",
        "data": {
            "core_features": [{
                "name": "Game Board",
                "description": "Interactive 3x3 grid for gameplay",
                "requirements": [
                    "Display 3x3 grid with clickable cells",
                    "Show X or O when cell is clicked",
                    "Prevent clicking on occupied cells"
                ],
                "priority": "high",
                "dependencies": ["React State Management"]
            }]
        }
    }
    return mock

@pytest.fixture
def mock_tavily_client():
    """Mock Tavily client for unit testing"""
    mock = Mock(spec=TavilyClient)
    mock.search = AsyncMock()
    return mock 