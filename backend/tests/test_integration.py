import pytest
from typing import Dict
import json
import time

def test_full_prd_generation_flow(agent_system, sample_project_data):
    """Test complete PRD generation flow"""
    lead_agent = agent_system["lead"]
    
    # Initialize project
    result = lead_agent.initialize_project(sample_project_data)
    assert result["status"] == "initialized"
    
    # Wait for initial research phase
    time.sleep(0.2)
    
    # Simulate research completion
    research_results = {
        "task_id": "research_1",
        "query": "user authentication",
        "results": {
            "main_findings": ["Use OAuth 2.0"],
            "sources": [{"title": "Auth Guide", "url": "example.com"}]
        }
    }
    
    lead_agent.handle_event({
        "type": "research_complete",
        "data": research_results
    })
    
    # Wait for feature definition
    time.sleep(0.2)
    
    # Verify memory storage
    memory_agent = agent_system["memory"]
    cursor = memory_agent.sql_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM features")
    feature_count = cursor.fetchone()[0]
    assert feature_count > 0

def test_agent_interaction_chain(agent_system, sample_project_data):
    """Test chain of agent interactions"""
    events_received = []
    
    def track_event(event):
        events_received.append(event)
    
    # Subscribe to relevant events
    agent_system["lead"].event_bus.subscribe("research_request", track_event)
    agent_system["lead"].event_bus.subscribe("feature_request", track_event)
    agent_system["lead"].event_bus.subscribe("validation_request", track_event)
    
    # Start the process
    agent_system["lead"].initialize_project(sample_project_data)
    
    # Wait for events
    time.sleep(0.3)
    
    # Verify event chain
    event_types = [e.type for e in events_received]
    assert "research_request" in event_types
    
    # Simulate research completion and verify feature definition starts
    agent_system["lead"].handle_event({
        "type": "research_complete",
        "data": {
            "task_id": "test_1",
            "results": {
                "main_findings": ["Key finding 1"],
                "sources": []
            }
        }
    })
    
    time.sleep(0.2)
    assert "feature_request" in [e.type for e in events_received]

def test_feedback_integration(agent_system, sample_project_data):
    """Test feedback integration across agents"""
    lead_agent = agent_system["lead"]
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
    
    # Track memory updates
    memory_updates = []
    def track_memory(event):
        if event.type == "update_memory":
            memory_updates.append(event)
    
    lead_agent.event_bus.subscribe("update_memory", track_memory)
    
    # Submit feedback
    lead_agent.handle_event({
        "type": "user_feedback",
        "data": feedback
    })
    
    # Wait for processing
    time.sleep(0.2)
    
    # Verify feedback was processed and stored
    assert len(memory_updates) > 0
    memory_agent = agent_system["memory"]
    cursor = memory_agent.sql_db.cursor()
    cursor.execute("SELECT * FROM features WHERE name = ?", ("Authentication",))
    feature = cursor.fetchone()
    assert feature is not None 