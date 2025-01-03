import pytest
import logging
from typing import List, Dict
from ...agents.validation_agent import ValidationAgent
from pubsub import pub
from ..base_test import BaseAgentTest
import time

logger = logging.getLogger(__name__)

class TestValidationAgent(BaseAgentTest):
    """Test cases for ValidationAgent"""
    
    def test_validation_agent_initialization(self, caplog):
        """Test validation agent initialization"""
        caplog.set_level(logging.DEBUG)
        logger.info("Testing validation agent initialization")
        
        agent = ValidationAgent()
        logger.debug(f"Created validation agent: {agent.name}")
        
        assert agent.name == "ValidationAgent"
        logger.info("Validation agent initialized successfully")

    def test_completeness_validation(self, sample_feature, sample_context, caplog):
        """Test feature completeness validation"""
        caplog.set_level(logging.DEBUG)
        logger.info("Testing feature completeness validation")
        
        agent = ValidationAgent()
        logger.debug("Created validation agent")
        
        logger.info(f"Validating feature: {sample_feature}")
        result = agent._check_completeness(sample_feature, sample_context)
        logger.debug(f"Validation result: {result}")
        
        assert "score" in result, "Result should contain a score"
        assert "feedback" in result, "Result should contain feedback"
        assert result["rule"] == "completeness"
        logger.info("Completeness validation completed successfully")

    def test_validation_process(self, sample_feature, sample_context, caplog):
        """Test complete validation process"""
        caplog.set_level(logging.DEBUG)
        logger.info("Testing complete validation process")
        
        agent = ValidationAgent()
        logger.debug("Created validation agent")
        
        self.subscribe_to_events(["validation_complete"])
        
        try:
            logger.info("Starting validation process")
            agent.validate_feature(sample_feature, sample_context)
            
            time.sleep(0.1)  # Add delay for event processing
            
            assert self.assert_event_received("validation_complete")[0], \
                "Should receive validation complete event"
            event = next(e for e in self.events_received if isinstance(e, dict) and e.get("type") == "validation_complete")
            assert "validation_results" in event["data"]["data"], \
                "Event should contain validation results"
            
        finally:
            self.cleanup_subscriptions() 