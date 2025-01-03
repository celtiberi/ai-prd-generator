import pytest
import logging
from unittest.mock import Mock, AsyncMock
from ...agents.feature_agent import FeatureAgent
from ...services.llm_service import LLMService
from pubsub import pub
from typing import Dict, Any, List
from ..base_test import BaseAgentTest

logger = logging.getLogger(__name__)

@pytest.fixture
def mock_llm_service() -> Mock:
    """Creates a mock LLM service for testing feature analysis"""
    mock = Mock(spec=LLMService)
    mock.structured_output = AsyncMock()
    mock.structured_output.return_value = {
        "status": "success",
        "data": {
            "name": "Game Board",
            "description": "Interactive 3x3 grid for gameplay",
            "requirements": [
                "Display 3x3 grid with clickable cells",
                "Show X or O when cell is clicked",
                "Prevent clicking on occupied cells"
            ],
            "priority": "high",
            "dependencies": ["React State Management"],
            "implementation_details": "Use React state to manage board"
        }
    }
    return mock

class TestFeatureAgent(BaseAgentTest):
    """Test cases for FeatureAgent"""
    
    @pytest.mark.asyncio
    async def test_feature_analysis(
        self,
        sample_feature_request: Dict[str, Any],
        mock_llm_service: Mock,
        caplog: pytest.LogCaptureFixture
    ) -> None:
        """Tests the feature analysis functionality of FeatureAgent"""
        caplog.set_level(logging.DEBUG)
        logger.info("Testing feature analysis")
        
        self.subscribe_to_events(["feature_defined"])
        
        try:
            logger.info("Creating FeatureAgent instance")
            agent = FeatureAgent(llm_service=mock_llm_service)
            
            logger.info("Starting feature analysis")
            result = await agent.analyze_feature(
                sample_feature_request["feature"],
                sample_feature_request["context"]
            )
            
            logger.debug(f"Analysis result: {result}")
            
            assert result["status"] == "success", "Feature analysis should return success status"
            assert self.assert_event_received("feature_defined")[0], \
                "Should receive feature defined event"
            assert self.events_received[0]["data"]["feature"]["name"] == "Game Board", \
                "Feature name should match input"
            
        finally:
            self.cleanup_subscriptions() 