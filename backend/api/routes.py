from fastapi import FastAPI, HTTPException
from typing import Dict, List, Optional
from pydantic import BaseModel
import json
from ..agents.lead_agent import LeadAgent
from ..agents.research_agent import ResearchAgent
from ..agents.feature_agent import FeatureAgent
from ..agents.validation_agent import ValidationAgent
from ..agents.memory_agent import MemoryAgent
from ..events.event_bus import EventBus

app = FastAPI(title="AI PRD Generator")

# Initialize event bus and agents
event_bus = EventBus()
agents = {
    "lead": LeadAgent(event_bus),
    "memory": MemoryAgent(event_bus),
    "research": ResearchAgent(event_bus, api_key="YOUR_TAVILY_API_KEY"),
    "feature": FeatureAgent(event_bus),
    "validation": ValidationAgent(event_bus)
}

# Pydantic models for request/response validation
class ProjectInit(BaseModel):
    title: str
    description: str
    objectives: List[str]

class ProjectFeedback(BaseModel):
    features: Optional[Dict] = None
    objectives: Optional[List[str]] = None

class ProjectProgress(BaseModel):
    status: str
    features: List[Dict]
    validation_results: Optional[List[Dict]] = None

@app.post("/api/init")
async def initialize_project(project_data: ProjectInit):
    """Initialize PRD generation"""
    try:
        result = agents["lead"].initialize_project(project_data.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback")
async def submit_feedback(feedback: ProjectFeedback):
    """Submit feedback for PRD refinement"""
    try:
        agents["lead"].handle_event({
            "type": "user_feedback",
            "data": feedback.dict()
        })
        return {"status": "feedback_received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/progress")
async def get_progress():
    """Get current PRD generation progress"""
    try:
        # Query memory agent for current state
        cursor = agents["memory"].sql_db.cursor()
        cursor.execute("""
            SELECT name, description, status 
            FROM features 
            ORDER BY id DESC
        """)
        features = [
            {"name": row[0], "description": row[1], "status": row[2]}
            for row in cursor.fetchall()
        ]
        
        return ProjectProgress(
            status="in_progress",
            features=features
        ).dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download")
async def download_prd():
    """Download the generated PRD"""
    try:
        # Query memory agent for all PRD data
        cursor = agents["memory"].sql_db.cursor()
        
        # Get features
        cursor.execute("SELECT * FROM features WHERE status = 'validated'")
        features = cursor.fetchall()
        
        # Get dependencies
        cursor.execute("SELECT * FROM dependencies")
        dependencies = cursor.fetchall()
        
        # Format PRD
        prd = {
            "features": features,
            "dependencies": dependencies,
            "generated_at": datetime.now().isoformat()
        }
        
        return prd
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 