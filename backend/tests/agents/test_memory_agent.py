import pytest
import logging
from pubsub import pub
import numpy as np
from ...agents.memory_agent import MemoryAgent
import tempfile
import os
from ..base_test import BaseAgentTest
import time

logger = logging.getLogger(__name__)

@pytest.fixture
def mock_settings_memory():
    """Mock settings for in-memory testing"""
    class MockSettings:
        VECTOR_DIM = 768
        SQLITE_DB_PATH = ":memory:"
        FAISS_INDEX_PATH = "test_index"
    return MockSettings()

@pytest.fixture
def mock_settings_file():
    """Mock settings for file-based testing"""
    temp_dir = tempfile.mkdtemp()
    class MockSettings:
        VECTOR_DIM = 768
        SQLITE_DB_PATH = os.path.join(temp_dir, "test.db")
        FAISS_INDEX_PATH = "test_index"
    return MockSettings()

class TestMemoryAgent(BaseAgentTest):
    """Test cases for MemoryAgent"""
    
    def test_memory_storage_in_memory(self, mock_settings_memory, caplog):
        """Test storing data in memory agent with in-memory database"""
        caplog.set_level(logging.DEBUG)
        logger.info("Testing in-memory storage")
        
        agent = MemoryAgent(mock_settings_memory)
        logger.debug("Created memory agent with in-memory settings")
        
        self.subscribe_to_events(["memory_updated"])
        
        try:
            test_data = {
                "type": "research",
                "text": '{"findings": "test findings"}',
                "name": "test_research"
            }
            
            logger.info(f"Storing test data: {test_data}")
            agent.store(test_data)
            
            time.sleep(0.1)
            
            assert self.assert_event_received("memory_updated")[0], \
                "Should receive memory update event"
                
        finally:
            self.cleanup_subscriptions()
    
    def test_memory_storage_file_based(self, mock_settings_file, caplog):
        """Test storing data in memory agent with file-based database"""
        caplog.set_level(logging.DEBUG)
        logger.info("Testing file-based storage")
        
        agent = MemoryAgent(mock_settings_file)
        logger.debug(f"Created memory agent with file path: {mock_settings_file.SQLITE_DB_PATH}")
        
        self.subscribe_to_events(["memory_updated"])
        
        try:
            test_data = {
                "type": "research",
                "text": '{"findings": "test findings"}',
                "name": "test_research"
            }
            
            logger.info(f"Storing test data: {test_data}")
            agent.store(test_data)
            
            time.sleep(0.1)
            
            assert self.assert_event_received("memory_updated")[0], \
                "Should receive memory update event"
            assert os.path.exists(mock_settings_file.SQLITE_DB_PATH), \
                "Database file should exist"
            
        finally:
            self.cleanup_subscriptions() 