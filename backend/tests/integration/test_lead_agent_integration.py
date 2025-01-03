import pytest
import logging
from ...agents.lead_agent import LeadAgent
from ...schemas.test_fixtures import TIC_TAC_TOE_SUMMARY, TODO_APP_SUMMARY
from ...schemas.project_schemas import validate_project_summary
from config.settings import Settings
import asyncio
from ..base_test import BaseAgentTest

logger = logging.getLogger(__name__)

# Use settings to check for API key
settings = Settings()
pytestmark = [
    pytest.mark.integration,  # Mark as integration test
    pytest.mark.skipif(
        not settings.OPENAI_API_KEY,
        reason="OPENAI_API_KEY not set"
    )
]

class TestLeadAgentIntegration(BaseAgentTest):
    """Integration tests for LeadAgent"""
    
    @pytest.mark.asyncio
    async def test_lead_agent_llm_analysis(self, caplog):
        """Integration test for LeadAgent's LLM analysis with real OpenAI"""
        caplog.set_level(logging.DEBUG)
        logger.info("Starting LLM analysis integration test")
        
        agent = LeadAgent()
        logger.debug("Created lead agent")
        
        start_time = asyncio.get_event_loop().time()
        
        # Verify the test fixture follows our schema
        assert validate_project_summary(TIC_TAC_TOE_SUMMARY), "Invalid project summary"
        logger.debug("Validated project summary")
        
        # Initialize with project summary
        logger.info("Initializing agent with project summary")
        result = await agent.initialize_from_summary(TIC_TAC_TOE_SUMMARY)
        
        elapsed = asyncio.get_event_loop().time() - start_time
        logger.info(f"LLM Analysis completed in {elapsed:.2f} seconds")
        logger.debug(f"Analysis Result: {result}")
        
        # Verify successful analysis
        assert result["status"] == "analysis_complete", "Analysis should complete successfully"
        analysis = result["analysis"]
        
        # Validate structure
        logger.info("Validating analysis structure")
        assert "core_features" in analysis
        assert "technical_requirements" in analysis
        assert "integration_points" in analysis
        assert "constraints" in analysis
        assert "success_metrics" in analysis
        
        # Validate core features
        logger.info("Validating core features")
        features = analysis["core_features"]
        assert len(features) > 0, "Should have at least one core feature"
        for feature in features:
            assert all(key in feature for key in [
                "name", "description", "requirements", "priority", "dependencies"
            ]), "Feature missing required fields"
            assert feature["priority"] in ["high", "medium", "low"], "Invalid priority"
            assert isinstance(feature["requirements"], list), "Requirements should be a list"
            assert len(feature["requirements"]) > 0, "Should have at least one requirement"
        
        logger.info("LLM analysis integration test completed successfully")

    @pytest.mark.asyncio
    async def test_lead_agent_different_project(self, caplog):
        """Test LLM analysis with a different project to verify flexibility"""
        caplog.set_level(logging.DEBUG)
        logger.info("Starting different project analysis test")
        
        agent = LeadAgent()
        logger.debug("Created lead agent")
        
        start_time = asyncio.get_event_loop().time()
        
        logger.info("Initializing agent with TODO app summary")
        result = await agent.initialize_from_summary(TODO_APP_SUMMARY)
        
        elapsed = asyncio.get_event_loop().time() - start_time
        logger.info(f"TODO App Analysis completed in {elapsed:.2f} seconds")
        logger.debug(f"Analysis result: {result}")
        
        assert result["status"] == "analysis_complete", "Analysis should complete successfully"
        analysis = result["analysis"]
        
        # Verify the analysis adapts to different project types
        logger.info("Validating project-specific features")
        features = analysis["core_features"]
        feature_names = [f["name"].lower() for f in features]
        feature_descriptions = [f["description"].lower() for f in features]
        
        # Check for task management functionality in either names or descriptions
        assert any("task" in name for name in feature_names), \
            "Should include task management"
        
        # More flexible view/organization validation
        has_organization = any(
            any(term in text for term in ["list", "view", "organize", "categorization"])
            for text in (feature_names + feature_descriptions)
        )
        assert has_organization, "Should include way to view/organize tasks"
        logger.info("Different project analysis test completed successfully") 