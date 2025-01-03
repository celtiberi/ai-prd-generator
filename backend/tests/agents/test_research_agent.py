import pytest
import logging
from unittest.mock import Mock, AsyncMock
from ...agents.research_agent import ResearchAgent
from tavily import TavilyClient
from pubsub import pub
from ..base_test import BaseAgentTest

logger = logging.getLogger(__name__)

@pytest.fixture
def mock_tavily_client():
    mock = Mock(spec=TavilyClient)
    mock.search = AsyncMock()
    return mock

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

class TestResearchAgent(BaseAgentTest):
    """Test cases for ResearchAgent"""
    
    @pytest.mark.asyncio
    async def test_research_agent_initialization(self, mock_tavily_client, caplog):
        """Test research agent initialization"""
        caplog.set_level(logging.DEBUG)
        logger.info("Testing research agent initialization")
        
        agent = ResearchAgent(tavily_client=mock_tavily_client)
        logger.debug("Created research agent with mock Tavily client")
        
        assert agent.tavily_client == mock_tavily_client
        logger.info("Research agent initialized successfully")

    @pytest.mark.asyncio
    async def test_tavily_search(self, mock_tavily_client, mock_tavily_response, caplog):
        """Test Tavily API search"""
        caplog.set_level(logging.DEBUG)
        logger.info("Testing Tavily API search")
        
        mock_tavily_client.search.return_value = mock_tavily_response
        agent = ResearchAgent(tavily_client=mock_tavily_client)
        logger.debug("Created research agent with mock Tavily client")
        
        query = "test query"
        logger.info(f"Executing search with query: {query}")
        result = await agent._search_tavily(query)
        
        logger.debug(f"Search result: {result}")
        assert result == mock_tavily_response
        mock_tavily_client.search.assert_called_once_with(query)
        logger.info("Tavily search test completed successfully")

    @pytest.mark.asyncio
    async def test_research_task_execution(self, mock_tavily_client, mock_tavily_response, caplog):
        """Test complete research task execution"""
        caplog.set_level(logging.DEBUG)
        logger.info("Testing research task execution")
        
        mock_tavily_client.search.return_value = mock_tavily_response
        agent = ResearchAgent(tavily_client=mock_tavily_client)
        logger.debug("Created research agent with mock Tavily client")
        
        self.subscribe_to_events(["research_complete"])
        
        try:
            task = {
                "task_id": "test_1",
                "query": "test query"
            }
            
            logger.info(f"Executing research task: {task}")
            result = await agent.execute_task(task)
            
            # Add small delay to allow event processing
            import asyncio
            await asyncio.sleep(0.1)
            
            assert result["status"] == "success", "Task should complete successfully"
            assert self.assert_event_received("research_complete")[0], \
                "Should receive research complete event"
                
        finally:
            self.cleanup_subscriptions() 