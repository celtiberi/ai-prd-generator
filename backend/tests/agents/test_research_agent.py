import pytest
from unittest.mock import patch, MagicMock
from ...agents.research_agent import ResearchAgent

@pytest.fixture
def mock_tavily_response():
    return {
        "results": [
            {
                "title": "Test Article",
                "url": "https://example.com",
                "snippet": "Relevant information",
                "relevance_score": 0.8
            }
        ]
    }

def test_research_agent_initialization(event_bus):
    """Test research agent initialization"""
    agent = ResearchAgent(event_bus, "test_api_key")
    assert agent.api_key == "test_api_key"
    assert len(agent.active_searches) == 0

@patch('aiohttp.ClientSession.post')
async def test_tavily_search(mock_post, event_bus, mock_tavily_response):
    """Test Tavily API search"""
    mock_post.return_value.__aenter__.return_value.json = MagicMock(
        return_value=mock_tavily_response
    )
    
    agent = ResearchAgent(event_bus, "test_api_key")
    result = await agent._search_tavily("test query")
    
    assert result == mock_tavily_response
    mock_post.assert_called_once()

def test_process_results(event_bus):
    """Test processing of search results"""
    agent = ResearchAgent(event_bus, "test_api_key")
    
    test_results = {
        "results": [
            {
                "title": "Test",
                "url": "https://example.com",
                "snippet": "Important info",
                "relevance_score": 0.9
            }
        ]
    }
    
    test_task = {
        "task_id": "test_1",
        "query": "test query",
        "context": "test context"
    }
    
    processed = agent._summarize_results(test_results)
    assert "main_findings" in processed
    assert "sources" in processed
    assert len(processed["sources"]) == 1

@pytest.mark.asyncio
async def test_research_task_execution(event_bus, mock_tavily_response):
    """Test complete research task execution"""
    agent = ResearchAgent(event_bus, "test_api_key")
    
    # Mock the Tavily search
    with patch.object(agent, '_search_tavily', return_value=mock_tavily_response):
        # Create a test task
        task = {
            "query": "test query",
            "context": "test context",
            "task_id": "test_1"
        }
        
        # Execute task
        await agent.execute_task(task)
        
        # Verify results were processed and published
        # (You might need to add result verification logic depending on your implementation) 