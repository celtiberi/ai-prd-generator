import pytest
import logging
from pubsub import pub
from ...agents.memory_agent import MemoryAgent
from ...agents.lead_agent import LeadAgent
from ...agents.research_agent import ResearchAgent
from ...agents.feature_agent import FeatureAgent
from ...agents.validation_agent import ValidationAgent
import time
from ..base_test import BaseAgentTest
import asyncio

logger = logging.getLogger(__name__)

class TestIntegration(BaseAgentTest):
    """Integration tests for the complete agent system"""
    
    @pytest.mark.asyncio
    async def test_full_prd_generation_flow(self, agent_system, sample_project_data, caplog):
        """Test complete PRD generation flow"""
        caplog.set_level(logging.DEBUG)
        logger.info("Testing full PRD generation flow")
        
        self.subscribe_to_events([
            "research_request",
            "feature_request"
        ])
        
        try:
            lead_agent = agent_system["lead"]
            logger.info("Initializing lead agent with project data")
            await lead_agent.initialize_from_summary(sample_project_data)
            
            # Add small delay to allow event processing
            await asyncio.sleep(0.1)
            
            # Verify events were published
            assert self.assert_event_received("research_request")[0], \
                "No research request event received"
            assert self.assert_event_received("feature_request")[0], \
                "No feature request event received"
                
        finally:
            self.cleanup_subscriptions()
    
    @pytest.mark.asyncio
    async def test_feedback_integration(self, agent_system, sample_project_data, caplog):
        """Test feedback integration across agents"""
        caplog.set_level(logging.DEBUG)
        logger.info("Testing feedback integration")
        
        lead_agent = agent_system["lead"]
        logger.debug("Initializing lead agent")
        lead_agent.initialize_project(sample_project_data)
        
        feedback = {
            "features": [{
                "name": "Authentication",
                "description": "User auth system",
                "requirements": ["OAuth 2.0"],
                "dependencies": [],
                "priority": "high",
                "status": "draft",
                "feedback": "Add MFA support"
            }]
        }
        
        self.subscribe_to_events(["memory_updated"])
        
        try:
            logger.info("Submitting feedback")
            await lead_agent.handle_event({
                "type": "user_feedback",
                "data": feedback
            })
            
            await asyncio.sleep(0.2)
            
            assert self.assert_event_received("memory_updated")[0], \
                "Should receive memory update event"
            
            # Verify feedback was stored
            memory_agent = agent_system["memory"]
            cursor = memory_agent.sql_db.cursor()
            cursor.execute("SELECT * FROM features WHERE name = ?", ("Authentication",))
            feature = cursor.fetchone()
            assert feature is not None, "Feature should be stored in database"
            
        finally:
            self.cleanup_subscriptions() 