import pytest
import logging
from unittest.mock import Mock
from ...agents.base_agent import BaseAgent
from pubsub import pub
from typing import Dict, Any, List
from ..base_test import BaseAgentTest

logger = logging.getLogger(__name__)

class TestAgent(BaseAgent):
    """Test implementation of BaseAgent"""
    def __init__(self, name: str):
        super().__init__(name)
        self.handled_events: List[Dict[str, Any]] = []

    def handle_event(self, event: Dict[str, Any]) -> None:
        self.handled_events.append(event)

    def execute_task(self, task: Dict[str, Any]) -> str:
        return f"Executed {task}"

class TestBaseAgent(BaseAgentTest):
    """Test cases for BaseAgent"""

    def test_base_agent_initialization(self, caplog):
        """Test agent initialization"""
        caplog.set_level(logging.DEBUG)
        logger.info("Testing base agent initialization")
        
        agent = TestAgent("test_agent")
        logger.debug(f"Created agent with name: {agent.name}")
        
        assert agent.name == "test_agent"

    def test_base_agent_event_handling(self, caplog):
        """Test event subscription and handling"""
        caplog.set_level(logging.DEBUG)
        logger.info("Testing base agent event handling")
        
        agent = TestAgent("test_agent")
        agent.subscribe("test_event")
        logger.debug("Subscribed agent to test_event")
        
        self.subscribe_to_events(["test_event"])
        
        try:
            test_data = {"message": "test"}
            logger.info(f"Publishing test event: {test_data}")
            agent.publish("test_event", test_data)
            
            assert self.assert_event_received("test_event")[0], \
                "Should receive test event"
            assert self.events_received[0]["data"]["message"] == "test"
            
        finally:
            self.cleanup_subscriptions()

    def test_base_agent_publishing(self, caplog):
        """Test event publishing"""
        caplog.set_level(logging.DEBUG)
        logger.info("Testing base agent publishing")
        
        agent = TestAgent("test_agent")
        logger.debug(f"Created agent: {agent.name}")
        
        self.subscribe_to_events(["test_event"])
        
        try:
            logger.info("Publishing test event")
            agent.publish("test_event", {"message": "test"})
            
            assert self.assert_event_received("test_event")[0], \
                "Should receive test event"
            assert self.events_received[0]["data"]["message"] == "test"
            
        finally:
            self.cleanup_subscriptions() 