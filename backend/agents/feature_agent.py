from typing import Dict, Any, List
from .base_agent import BaseAgent
import json
from dataclasses import dataclass
from typing import Optional

@dataclass
class Feature:
    name: str
    description: str
    requirements: List[str]
    dependencies: List[str]
    priority: str
    status: str = "draft"
    feedback: Optional[str] = None

class FeatureAgent(BaseAgent):
    def __init__(self, event_bus):
        super().__init__("FeatureAgent", event_bus)
        self.current_context = None
        self.research_data = {}
        
        # Subscribe to events
        self.subscribe("feature_request")
        self.subscribe("memory_updated")

    def handle_event(self, event):
        if event.type == "feature_request":
            self.current_context = event.data["context"]
            self._start_feature_definition(event.data)
        elif event.type == "memory_updated" and event.data["type"] == "research":
            self._update_research_data(event.data)

    def _start_feature_definition(self, data: Dict):
        """Start defining features based on context and research"""
        if "feedback" in data:
            self._refine_features(data["feedback"])
        else:
            self._define_new_features()

    def _define_new_features(self):
        """Define new features based on project context and research"""
        features = []
        
        # Extract requirements from objectives
        for objective in self.current_context.objectives:
            feature = self._create_feature_from_objective(objective)
            features.append(feature)
            
        # Publish each feature for validation
        for feature in features:
            self.publish("feature_defined", {
                "feature": feature.__dict__,
                "context": self.current_context
            })

    def _create_feature_from_objective(self, objective: str) -> Feature:
        """Create a feature definition from an objective"""
        # Here we would use the research data to inform feature creation
        requirements = self._extract_requirements(objective)
        dependencies = self._identify_dependencies(requirements)
        
        return Feature(
            name=self._generate_feature_name(objective),
            description=objective,
            requirements=requirements,
            dependencies=dependencies,
            priority=self._determine_priority(objective)
        )

    def _extract_requirements(self, objective: str) -> List[str]:
        """Extract technical requirements from an objective"""
        requirements = []
        relevant_research = self._find_relevant_research(objective)
        
        # Use research data to identify technical requirements
        for research in relevant_research:
            for finding in research.get("main_findings", []):
                if self._is_requirement(finding):
                    requirements.append(finding)
        
        return requirements

    def _identify_dependencies(self, requirements: List[str]) -> List[str]:
        """Identify dependencies for a set of requirements"""
        dependencies = []
        # Analyze requirements to identify technical dependencies
        # This would use the research data to inform dependency identification
        return dependencies

    def _determine_priority(self, objective: str) -> str:
        """Determine feature priority based on context and dependencies"""
        # Simple priority determination logic
        if any(kw in objective.lower() for kw in ["critical", "essential", "core"]):
            return "high"
        elif any(kw in objective.lower() for kw in ["should", "would be nice"]):
            return "medium"
        return "low"

    def _refine_features(self, feedback: Dict):
        """Refine features based on validation feedback"""
        feature = Feature(**feedback["feature"])
        feature.feedback = feedback.get("feedback", "")
        feature.status = "refined"
        
        # Publish refined feature for validation
        self.publish("feature_defined", {
            "feature": feature.__dict__,
            "context": self.current_context
        })

    def _update_research_data(self, data: Dict):
        """Update local research data cache"""
        research_data = json.loads(data["text"])
        self.research_data[data["name"]] = research_data

    def _find_relevant_research(self, objective: str) -> List[Dict]:
        """Find research relevant to an objective"""
        relevant_research = []
        for research in self.research_data.values():
            if self._is_relevant(research, objective):
                relevant_research.append(research)
        return relevant_research

    def _is_relevant(self, research: Dict, objective: str) -> bool:
        """Determine if research is relevant to an objective"""
        # Simple relevance check based on keyword matching
        objective_keywords = set(objective.lower().split())
        research_text = research.get("query", "").lower()
        return any(keyword in research_text for keyword in objective_keywords)

    def _is_requirement(self, finding: str) -> bool:
        """Determine if a research finding represents a requirement"""
        requirement_indicators = ["must", "should", "requires", "needs", "necessary"]
        return any(indicator in finding.lower() for indicator in requirement_indicators)

    def _generate_feature_name(self, objective: str) -> str:
        """Generate a concise feature name from an objective"""
        # Simple name generation - take first few words
        words = objective.split()
        return " ".join(words[:3]).title() 