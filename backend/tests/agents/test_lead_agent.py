import pytest
import logging
from unittest.mock import Mock, AsyncMock
from ...agents.lead_agent import LeadAgent
from ...services.llm_service import LLMService
from ...schemas.project_schemas import validate_project_summary
from ...schemas.test_fixtures import TIC_TAC_TOE_SUMMARY
from ..base_test import BaseAgentTest

logger = logging.getLogger(__name__)

class TestLeadAgent(BaseAgentTest):
    """Test cases for LeadAgent"""
    
    @pytest.mark.asyncio
    async def test_feature_delegation(self, sample_project_summary, mock_llm_service, caplog):
        """Test feature delegation to feature agents"""
        caplog.set_level(logging.DEBUG)
        logger.info("Testing feature delegation")
        
        self.subscribe_to_events(["feature_request"])
        
        try:
            agent = LeadAgent(llm_service=mock_llm_service)
            logger.debug("Created lead agent with mock LLM service")
            
            await agent.initialize_from_summary(sample_project_summary)
            logger.info("Initialized agent with project summary")
            
            assert self.assert_event_received("feature_request")[0], \
                "Should receive feature request event"
            assert self.events_received[0]["data"]["feature"]["name"] == "Game Board"
            
        finally:
            self.cleanup_subscriptions()

    @pytest.mark.asyncio
    async def test_analysis_failure_handling(self, sample_project_summary, mock_llm_service, caplog):
        """Test handling of analysis failures"""
        caplog.set_level(logging.DEBUG)
        
        self.subscribe_to_events(["feature_request"])
        
        try:
            async def mock_failed_analysis(*args, **kwargs):
                return {
                    "status": "error",
                    "error": "Analysis failed"
                }
            
            mock_llm_service.structured_output.side_effect = mock_failed_analysis
            
            agent = LeadAgent(llm_service=mock_llm_service)
            result = await agent.initialize_from_summary(sample_project_summary)
            
            assert result["status"] == "analysis_failed"
            assert "error" in result
            assert not self.events_received, "No features should be delegated"
            
        finally:
            self.cleanup_subscriptions() 