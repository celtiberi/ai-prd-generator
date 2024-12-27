import pytest
import numpy as np
from ...agents.memory_agent import MemoryAgent

def test_memory_agent_initialization(event_bus, mock_settings):
    """Test memory agent initialization"""
    agent = MemoryAgent(event_bus, mock_settings)
    assert agent.vector_dim == mock_settings.VECTOR_DIM
    assert agent.vector_db is not None
    assert agent.sql_db is not None

def test_memory_storage(event_bus, mock_settings):
    """Test storing data in memory agent"""
    agent = MemoryAgent(event_bus, mock_settings)
    
    test_data = {
        "type": "research",
        "text": '{"findings": "test findings"}',
        "name": "test_research"
    }
    
    # Store data
    agent.store(test_data)
    
    # Verify storage in SQLite
    cursor = agent.sql_db.cursor()
    cursor.execute("SELECT * FROM features WHERE name = ?", (test_data["name"],))
    result = cursor.fetchone()
    assert result is not None
    assert result[1] == test_data["name"]

def test_vector_search(event_bus, mock_settings):
    """Test vector search functionality"""
    agent = MemoryAgent(event_bus, mock_settings)
    
    # Add test vectors
    test_text = "test document for search"
    embedding = agent._generate_embedding(test_text)
    agent.vector_db.add(np.array([embedding]).astype('float32'))
    
    # Search
    query = "test document"
    distances, indices = agent.search_similar(query, k=1)
    assert len(distances) == 1
    assert len(indices) == 1

def test_event_handling(event_bus, mock_settings):
    """Test memory agent event handling"""
    agent = MemoryAgent(event_bus, mock_settings)
    
    test_event = {
        "type": "update_memory",
        "data": {
            "type": "research",
            "text": '{"findings": "test findings"}',
            "name": "test_research"
        }
    }
    
    # Create event
    agent.handle_event(test_event)
    
    # Verify storage
    cursor = agent.sql_db.cursor()
    cursor.execute("SELECT * FROM features WHERE name = ?", (test_event["data"]["name"],))
    result = cursor.fetchone()
    assert result is not None

@pytest.mark.asyncio
async def test_concurrent_storage(event_bus, mock_settings):
    """Test concurrent storage operations"""
    agent = MemoryAgent(event_bus, mock_settings)
    
    import asyncio
    
    async def store_data(index):
        data = {
            "type": "research",
            "text": f'{{"findings": "test findings {index}"}}',
            "name": f"test_research_{index}"
        }
        agent.store(data)
    
    # Store multiple items concurrently
    await asyncio.gather(*[store_data(i) for i in range(5)])
    
    # Verify all items were stored
    cursor = agent.sql_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM features")
    count = cursor.fetchone()[0]
    assert count == 5 