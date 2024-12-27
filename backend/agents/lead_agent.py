from typing import Dict, Any, List
from .base_agent import BaseAgent
from dataclasses import dataclass
import json

@dataclass
class ProjectContext:
    title: str
    description: str
    objectives: List[str]
    status: str = "initializing"

class LeadAgent(BaseAgent):
    def __init__(self, event_bus):
        super().__init__("LeadAgent", event_bus)
        self.project_context = None
        self.active_tasks: Dict[str, Any] = {}
        
        # Subscribe to relevant events
        self.subscribe("research_complete")
        self.subscribe("feature_defined")
        self.subscribe("validation_complete")
        self.subscribe("user_feedback")

    def initialize_project(self, project_data: dict):
        """Initialize a new PRD generation project"""
        self.project_context = ProjectContext(
            title=project_data.get('title', ''),
            description=project_data.get('description', ''),
            objectives=project_data.get('objectives', [])
        )
        
        # Start the PRD generation workflow
        self._start_research_phase()
        return {"status": "initialized", "project": self.project_context}

    def _start_research_phase(self):
        """Initiate the research phase by delegating to Research Agents"""
        research_tasks = self._generate_research_tasks()
        for task in research_tasks:
            self.publish("research_request", {
                "query": task,
                "context": self.project_context.title,
                "task_id": f"research_{len(self.active_tasks)}"
            }, target="ResearchAgent")
            
    def _generate_research_tasks(self) -> List[str]:
        """Generate research tasks based on project context"""
        tasks = []
        # Add core research tasks
        tasks.append(f"Technical requirements for {self.project_context.title}")
        tasks.append(f"Best practices for {self.project_context.title}")
        
        # Add objective-specific research tasks
        for objective in self.project_context.objectives:
            tasks.append(f"Implementation approaches for: {objective}")
            
        return tasks

    def handle_event(self, event):
        """Handle various events from other agents"""
        handlers = {
            "research_complete": self._handle_research_complete,
            "feature_defined": self._handle_feature_defined,
            "validation_complete": self._handle_validation_complete,
            "user_feedback": self._handle_user_feedback
        }
        
        if event.type in handlers:
            handlers[event.type](event.data)

    def _handle_research_complete(self, data: dict):
        """Process completed research and initiate feature definition"""
        # Store research results
        self.publish("update_memory", {
            "type": "research",
            "text": json.dumps(data["results"]),
            "name": data["task_id"]
        })
        
        # Check if all research is complete
        if self._is_research_phase_complete():
            self._start_feature_definition()

    def _handle_feature_defined(self, data: dict):
        """Process defined features and initiate validation"""
        self.publish("validation_request", {
            "feature": data["feature"],
            "context": self.project_context
        }, target="ValidationAgent")

    def _handle_validation_complete(self, data: dict):
        """Process validation results and update PRD accordingly"""
        if data["status"] == "valid":
            self.publish("update_memory", {
                "type": "feature",
                "text": json.dumps(data["feature"]),
                "name": data["feature"]["name"],
                "status": "validated"
            })
        else:
            # Reinitiate feature definition with feedback
            self.publish("feature_request", {
                "context": self.project_context,
                "feedback": data["feedback"]
            }, target="FeatureAgent")

    def _handle_user_feedback(self, data: dict):
        """Process user feedback and adjust PRD generation"""
        self.project_context.status = "updating"
        # Trigger relevant updates based on feedback
        if "features" in data:
            self._handle_feature_feedback(data["features"])
        if "objectives" in data:
            self._update_objectives(data["objectives"])

    def _is_research_phase_complete(self) -> bool:
        """Check if all research tasks are complete"""
        # Implementation depends on how we're tracking tasks
        return len([t for t in self.active_tasks.values() if t["type"] == "research"]) == 0

    def _start_feature_definition(self):
        """Initiate the feature definition phase"""
        self.project_context.status = "defining_features"
        self.publish("feature_request", {
            "context": self.project_context
        }, target="FeatureAgent") 