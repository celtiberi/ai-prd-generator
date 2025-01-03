from typing import Dict, Any, List
from .base_agent import BaseAgent
from dataclasses import dataclass
from ..services.llm_service import LLMService
from .memory_agent import MemoryAgent
import json
import uuid
from schemas.project_schemas import FEATURE_ANALYSIS_SCHEMA, validate_project_summary

@dataclass
class ProjectContext:
    summary: Dict[str, Any]
    analysis: Dict[str, Any] = None
    status: str = "initializing"

    def to_dict(self) -> Dict:
        return {
            "original_summary": self.summary,
            "analysis": self.analysis,
            "status": self.status
        }

class LeadAgent(BaseAgent):
    def __init__(self, llm_service=None, settings=None):
        super().__init__("LeadAgent")
        self.llm = llm_service or LLMService()
        self.project_context = None
        self.settings = settings
        self.log(f"Initialized with settings: {settings}")

    async def handle_event(self, event: Dict[str, Any]) -> None:
        """Handle incoming events"""
        if event["type"] == "project_summary_ready":
            await self.initialize_from_summary(event["data"])
        elif event["type"] == "research_complete":
            await self._process_research_results(event["data"])
        elif event["type"] == "feature_defined":
            await self._process_feature_definition(event["data"])
        elif event["type"] == "validation_complete":
            await self._process_validation_results(event["data"])
        elif event["type"] == "user_feedback":
            # Handle user feedback
            if not self.settings:
                self.log(f"Settings missing: {self.settings}")
                raise ValueError("Settings required for memory operations")
            memory_agent = MemoryAgent(self.settings)
            # Store each feature from the feedback
            for feature in event["data"]["features"]:
                memory_agent.store(feature)  # Store individual feature instead of whole feedback object

    async def initialize_from_summary(self, project_summary: Dict[str, Any]):
        """Initialize project from summary and delegate features"""
        try:
            self.project_context = project_summary
            
            # Request initial research
            self.publish("research_request", {
                "query": f"Best practices and patterns for {project_summary['title']}",
                "context": project_summary
            })
            
            # Start feature analysis
            response = await self.llm.structured_output(
                messages=[{
                    "role": "user",
                    "content": f"Analyze this project and break it down into features:\n{json.dumps(project_summary, indent=2)}"
                }],
                output_schema=FEATURE_ANALYSIS_SCHEMA
            )
            
            if response["status"] == "success":
                analysis = response["data"]
                
                # Delegate features to feature agents
                for feature in analysis["core_features"]:
                    self.publish("feature_request", {
                        "feature": feature,
                        "context": self.project_context
                    })
                
                return {
                    "status": "analysis_complete",
                    "analysis": analysis
                }
            else:
                return {
                    "status": "analysis_failed",
                    "error": response.get("error", "Unknown error")
                }
                
        except Exception as e:
            print(f"Error in initialize_from_summary: {str(e)}")
            return {
                "status": "analysis_failed",
                "error": str(e)
            }

    async def _process_research_results(self, data: Dict[str, Any]):
        """Process research results and update project context"""
        # Implementation here

    async def _process_feature_definition(self, data: Dict[str, Any]):
        """Process completed feature definitions"""
        # Implementation here

    async def _process_validation_results(self, data: Dict[str, Any]):
        """Process validation results for features"""
        # Implementation here 

    def initialize_project(self, project_data: Dict[str, Any]) -> None:
        """Initialize project with basic data before analysis"""
        self.project_data = project_data
        self.log(f"Initializing project with settings: {self.settings}")
        self.publish("project_initialized", {
            "project": project_data
        }) 