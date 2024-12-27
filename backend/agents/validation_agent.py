from typing import Dict, Any, List, Tuple
from .base_agent import BaseAgent
import json

class ValidationAgent(BaseAgent):
    def __init__(self, event_bus):
        super().__init__("ValidationAgent", event_bus)
        self.validation_rules = self._initialize_validation_rules()
        
        # Subscribe to validation requests
        self.subscribe("validation_request")

    def _initialize_validation_rules(self) -> List[Dict]:
        """Initialize validation rules for features"""
        return [
            {
                "name": "completeness",
                "check": self._check_completeness,
                "weight": 0.3
            },
            {
                "name": "consistency",
                "check": self._check_consistency,
                "weight": 0.3
            },
            {
                "name": "feasibility",
                "check": self._check_feasibility,
                "weight": 0.4
            }
        ]

    def handle_event(self, event):
        if event.type == "validation_request":
            self._validate_feature(event.data)

    def _validate_feature(self, data: Dict):
        """Validate a feature definition"""
        feature = data["feature"]
        context = data["context"]
        
        validation_results = []
        total_score = 0.0
        
        # Apply each validation rule
        for rule in self.validation_rules:
            score, feedback = rule["check"](feature, context)
            weighted_score = score * rule["weight"]
            total_score += weighted_score
            
            validation_results.append({
                "rule": rule["name"],
                "score": score,
                "feedback": feedback
            })

        # Determine if feature is valid based on total score
        is_valid = total_score >= 0.7
        
        self._publish_validation_results(
            feature, is_valid, validation_results, context
        )

    def _check_completeness(self, feature: Dict, context: Dict) -> Tuple[float, str]:
        """Check if feature definition is complete"""
        required_fields = ["name", "description", "requirements", "dependencies"]
        missing_fields = [field for field in required_fields if not feature.get(field)]
        
        if missing_fields:
            return 0.0, f"Missing required fields: {', '.join(missing_fields)}"
            
        # Check content quality
        score = 1.0
        feedback = []
        
        if len(feature["description"]) < 50:
            score -= 0.3
            feedback.append("Description is too brief")
            
        if not feature["requirements"]:
            score -= 0.4
            feedback.append("No requirements specified")
            
        return score, "; ".join(feedback) if feedback else "Complete"

    def _check_consistency(self, feature: Dict, context: Dict) -> Tuple[float, str]:
        """Check if feature is consistent with project context"""
        score = 1.0
        feedback = []
        
        # Check if feature aligns with objectives
        aligned_with_objectives = any(
            self._text_similarity(feature["description"], obj) > 0.3
            for obj in context.objectives
        )
        
        if not aligned_with_objectives:
            score -= 0.5
            feedback.append("Feature doesn't align with project objectives")
            
        # Check internal consistency
        if not self._check_requirements_consistency(feature):
            score -= 0.3
            feedback.append("Requirements are not consistent with feature description")
            
        return score, "; ".join(feedback) if feedback else "Consistent"

    def _check_feasibility(self, feature: Dict, context: Dict) -> Tuple[float, str]:
        """Check if feature is technically feasible"""
        score = 1.0
        feedback = []
        
        # Check dependencies
        if feature["dependencies"]:
            if not self._check_dependencies_feasibility(feature["dependencies"]):
                score -= 0.4
                feedback.append("Some dependencies may not be feasible")
        
        # Check technical complexity
        complexity_score = self._assess_technical_complexity(feature)
        if complexity_score > 0.8:
            score -= 0.3
            feedback.append("Feature may be too complex to implement")
            
        return score, "; ".join(feedback) if feedback else "Feasible"

    def _publish_validation_results(
        self, feature: Dict, is_valid: bool, 
        validation_results: List[Dict], context: Dict
    ):
        """Publish validation results"""
        if is_valid:
            self.publish("validation_complete", {
                "status": "valid",
                "feature": feature,
                "validation_results": validation_results
            })
        else:
            self.publish("validation_complete", {
                "status": "invalid",
                "feature": feature,
                "validation_results": validation_results,
                "feedback": self._generate_feedback(validation_results)
            })

    def _generate_feedback(self, validation_results: List[Dict]) -> str:
        """Generate actionable feedback from validation results"""
        feedback = []
        for result in validation_results:
            if result["score"] < 0.7:
                feedback.append(f"{result['rule'].title()}: {result['feedback']}")
        return "; ".join(feedback)

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity (simple implementation)"""
        # This would be replaced with a more sophisticated similarity calculation
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0.0

    def _check_requirements_consistency(self, feature: Dict) -> bool:
        """Check if requirements are consistent with feature description"""
        # Simple implementation - could be enhanced with NLP
        return all(
            self._text_similarity(req, feature["description"]) > 0.1
            for req in feature["requirements"]
        )

    def _check_dependencies_feasibility(self, dependencies: List[str]) -> bool:
        """Check if dependencies are feasible"""
        # This would typically check against known available technologies/components
        return True  # Simplified implementation

    def _assess_technical_complexity(self, feature: Dict) -> float:
        """Assess technical complexity of a feature"""
        # Simple complexity assessment based on requirements and dependencies
        complexity = 0.0
        complexity += len(feature["requirements"]) * 0.1
        complexity += len(feature["dependencies"]) * 0.15
        return min(complexity, 1.0) 