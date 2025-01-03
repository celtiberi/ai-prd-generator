from typing import Dict, Any, List
from .base_agent import BaseAgent
from dataclasses import dataclass
from ..services.llm_service import LLMService
from .memory_agent import MemoryAgent
import json
import yaml
from pathlib import Path
from schemas.project_schemas import FEATURE_ANALYSIS_SCHEMA, validate_project_summary

@dataclass
class ProjectContext:
    summary: Dict[str, Any]
    analysis: Dict[str, Any] = None
    status: str = "initializing"
    documentation_path: str = ".notes"
    features_status: Dict[str, str] = None  # Track status of each feature
    validation_feedback: Dict[str, List[str]] = None  # Store validation feedback

    def __post_init__(self):
        self.features_status = {}
        self.validation_feedback = {}

    def to_dict(self) -> Dict:
        return {
            "original_summary": self.summary,
            "analysis": self.analysis,
            "status": self.status,
            "documentation_path": self.documentation_path,
            "features_status": self.features_status,
            "validation_feedback": self.validation_feedback
        }

class LeadAgent(BaseAgent):
    def __init__(self, llm_service=None, settings=None):
        super().__init__("LeadAgent")
        self.llm = llm_service or LLMService()
        self.project_context = None
        self.settings = settings
        
        # Define expected documentation structure
        self.documentation_structure = {
            "project.prd.md": {
                "description": "High-level project overview with links to detailed docs",
                "format": "YAML-based markdown",
                "sections": ["core_objectives", "agent_workflow", "key_documents", "status"]
            },
            "component_architecture.md": {
                "description": "Component relationships and interactions",
                "format": "YAML + Mermaid diagrams",
                "sections": ["components", "workflows", "interaction_flow"]
            },
            "development_guidelines.md": {
                "description": "Development standards and practices",
                "format": "YAML-based guidelines"
            },
            "testing_guidelines.md": {
                "description": "Testing standards and organization",
                "format": "YAML-based testing rules"
            },
            "changelog.md": {
                "description": "Version history and planned features",
                "format": "YAML-based changelog"
            }
        }

    async def initialize_from_summary(self, project_summary: Dict[str, Any]):
        """Initialize project from consultant's summary and begin feature development process"""
        try:
            self.project_context = ProjectContext(summary=project_summary)
            self.log("Initializing project from consultant summary")
            
            # Analyze project for feature breakdown
            features_response = await self.llm.structured_output(
                messages=[{
                    "role": "system",
                    "content": "Break down the project into discrete features for development."
                }, {
                    "role": "user",
                    "content": f"Project Summary:\n{yaml.dump(project_summary)}"
                }],
                output_schema=FEATURE_ANALYSIS_SCHEMA
            )
            
            if features_response["status"] == "success":
                features = features_response["data"]["core_features"]
                
                # Initialize feature tracking
                for feature in features:
                    self.project_context.features_status[feature["name"]] = "assigned"
                
                # Delegate features to feature agents
                for feature in features:
                    self.publish("feature_request", {
                        "feature": feature,
                        "context": self.project_context.to_dict(),
                        "requirements": project_summary.get("requirements", {})
                    })
                
                self.log(f"Delegated {len(features)} features to feature agents")
                return {
                    "status": "features_delegated",
                    "feature_count": len(features)
                }
            else:
                return {
                    "status": "analysis_failed",
                    "error": features_response.get("error", "Unknown error in feature analysis")
                }
                
        except Exception as e:
            self.log(f"Error in initialize_from_summary: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def handle_event(self, event: Dict[str, Any]):
        """Handle various events in the feature development pipeline"""
        event_type = event.get("type")
        
        if event_type == "feature_completed":
            await self._handle_feature_completion(event["data"])
        elif event_type == "validation_result":
            await self._handle_validation_result(event["data"])
        elif event_type == "research_complete":
            await self._handle_research_results(event["data"])
        
        # Check if all features are complete
        if self._all_features_complete():
            await self._generate_documentation()

    async def _handle_feature_completion(self, data: Dict[str, Any]):
        """Process a completed feature from a feature agent"""
        feature_name = data["feature"]["name"]
        self.project_context.features_status[feature_name] = "completed"
        
        # Request validation
        self.publish("validation_request", {
            "feature": data["feature"],
            "context": self.project_context.to_dict()
        })

    async def _handle_validation_result(self, data: Dict[str, Any]):
        """Process validation results for a feature"""
        feature_name = data["feature"]["name"]
        if data["status"] == "valid":
            self.project_context.features_status[feature_name] = "validated"
        else:
            self.project_context.features_status[feature_name] = "needs_revision"
            self.project_context.validation_feedback[feature_name] = data["feedback"]
            
            # Request feature revision
            self.publish("feature_revision", {
                "feature": data["feature"],
                "feedback": data["feedback"],
                "context": self.project_context.to_dict()
            })

    async def _generate_documentation(self):
        """Generate all project documentation once features are complete"""
        try:
            docs_path = Path(self.project_context.documentation_path)
            
            # Generate each document based on our structure
            for doc_name, config in self.documentation_structure.items():
                doc_content = await self._generate_document(doc_name, config)
                doc_path = docs_path / doc_name
                doc_path.write_text(doc_content)
            
            self.log("Documentation generation complete")
            self.publish("documentation_complete", {
                "status": "success",
                "path": str(docs_path)
            })
            
        except Exception as e:
            self.log(f"Error generating documentation: {str(e)}")
            self.publish("documentation_complete", {
                "status": "error",
                "error": str(e)
            })

    def _all_features_complete(self) -> bool:
        """Check if all features are validated"""
        return all(status == "validated" 
                  for status in self.project_context.features_status.values()) 