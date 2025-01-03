import pytest
import logging
from ...agents.project_consultant_agent import ProjectConsultantAgent
from ...schemas.project_schemas import validate_project_summary
from config.settings import Settings
import asyncio
from ..base_test import BaseAgentTest
import json

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

class TestProjectConsultant(BaseAgentTest):
    """Integration tests for ProjectConsultantAgent"""
    
    @pytest.mark.asyncio
    async def test_conversation_to_structured_summary(self, caplog):
        """Test converting a conversation into a structured summary"""
        caplog.set_level(logging.DEBUG)
        logger.info("Starting conversation to summary test")
        
        agent = ProjectConsultantAgent()
        logger.debug("Created project consultant agent")
        
        start_time = asyncio.get_event_loop().time()
        
        conversation = [
            "I want to build a Tic Tac Toe game to learn React",
            "It should be interactive and fun to play",
            "I want to help new React developers learn state management",
            "It needs features like move history and undo"
        ]
        logger.info(f"Processing conversation with {len(conversation)} messages")
        
        self.subscribe_to_events(["summary_updated"])
        
        try:
            # Process messages concurrently
            logger.debug("Starting concurrent message processing")
            tasks = [agent.process_message(msg) for msg in conversation]
            results = await asyncio.gather(*tasks)
            
            for msg, result in zip(conversation, results):
                logger.debug(f"Message: {msg}")
                logger.debug(f"Result: {result}")
                
                if result.get("status") == "error":
                    error_data = json.loads(result["message"].split(" - ", 1)[1])
                    if self.is_quota_exceeded(error_data):
                        pytest.skip("API quota exceeded")
                    
                assert result["status"] in ["consulting", "review_summary"], \
                    "Invalid response status"
                
                if result["status"] == "review_summary":
                    summary = result["summary"]
                    logger.info("Received project summary")
                    logger.debug(f"Summary content: {summary}")
                    
                    # Validate against schema
                    assert validate_project_summary(summary), "Summary should match schema"
                    
                    # Additional validation
                    assert "React" in summary["description"], \
                        "Summary should mention React"
                    assert any("state" in goal.lower() for goal in summary["goals"]), \
                        "Goals should mention state management"
                    assert any("history" in feature.lower() 
                             for feature in summary["key_features"]), \
                        "Features should include history functionality"
            
            elapsed = asyncio.get_event_loop().time() - start_time
            logger.info(f"Conversation processing completed in {elapsed:.2f} seconds")
            
        finally:
            self.cleanup_subscriptions()

    @pytest.mark.asyncio
    async def test_incremental_summary_building(self, caplog):
        """Test building summary incrementally through conversation"""
        caplog.set_level(logging.DEBUG)
        logger.info("Starting incremental summary building test")
        
        agent = ProjectConsultantAgent()
        logger.debug("Created project consultant agent")
        
        messages = [
            "I want to create a task management app",
            "It should help teams collaborate on projects",
            "Need features for assigning tasks and tracking progress"
        ]
        
        self.subscribe_to_events(["summary_updated"])
        
        try:
            for i, message in enumerate(messages, 1):
                logger.info(f"Processing message {i}/{len(messages)}")
                logger.debug(f"Message content: {message}")
                
                result = await agent.process_message(message)
                logger.debug(f"Processing result: {result}")
                
                if result["status"] == "review_summary":
                    summary = result["summary"]
                    logger.info("Received interim summary")
                    logger.debug(f"Summary state: {summary}")
                    
                    assert validate_project_summary(summary), \
                        "Interim summary should be valid"
                    
                    # Verify summary evolves with conversation
                    if "task" in message.lower():
                        assert any("task" in feature.lower() 
                                  for feature in summary["key_features"]), \
                            "Features should reflect task management"
                    if "team" in message.lower():
                        assert any("team" in user.lower() 
                                  for user in summary["target_users"]), \
                            "Users should include teams"
            
            logger.info("Incremental summary building test completed successfully")
            
        finally:
            self.cleanup_subscriptions() 