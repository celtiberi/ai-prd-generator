from typing import Dict, Any, List
from .base_agent import BaseAgent

class ValidationAgent(BaseAgent):
    def __init__(self):
        super().__init__("ValidationAgent")
        self.subscribe("validation_request")

    def handle_event(self, event):
        """Handle validation requests"""
        if event["type"] == "validation_request":
            feature = event["data"]["feature"]
            context = event["data"]["context"]
            
            # Run validation checks
            validation_results = []
            validation_results.append(self._check_completeness(feature, context))
            validation_results.append(self._check_consistency(feature, context))
            validation_results.append(self._check_feasibility(feature, context))
            
            # Generate feedback
            feedback = self._generate_feedback(validation_results)
            
            # Publish results using BaseAgent's publish
            self.publish("validation_complete", {
                "type": "validation_complete",
                "data": {
                    "feature": feature["name"],
                    "results": validation_results,
                    "feedback": feedback
                }
            })

    def _check_completeness(self, feature: Dict[str, Any], context: Dict[str, Any]):
        """Check if feature has all required fields"""
        score = 1.0
        feedback = []
        
        required_fields = ["name", "description", "requirements", "priority"]
        for field in required_fields:
            if field not in feature:
                score *= 0.5
                feedback.append(f"Missing {field}")
        
        return {
            "rule": "completeness",
            "score": score,
            "feedback": feedback
        }

    def _check_consistency(self, feature: Dict[str, Any], context: Dict[str, Any]):
        """Check if feature is consistent with project context"""
        score = 1.0
        feedback = []
        
        # Check priority levels
        valid_priorities = ["high", "medium", "low"]
        if feature.get("priority") not in valid_priorities:
            score *= 0.7
            feedback.append("Invalid priority level")
        
        return {
            "rule": "consistency",
            "score": score,
            "feedback": feedback
        }

    def _check_feasibility(self, feature: Dict[str, Any], context: Dict[str, Any]):
        """Check if feature implementation is feasible"""
        score = 1.0
        feedback = []
        
        # Check dependencies
        if "dependencies" in feature and feature["dependencies"]:
            # Simple check - more complex validation would go here
            score *= 0.9
            feedback.append("Has dependencies that need verification")
        
        return {
            "rule": "feasibility",
            "score": score,
            "feedback": feedback
        }

    def _generate_feedback(self, validation_results: List[Dict[str, Any]]) -> str:
        """Generate actionable feedback from validation results"""
        feedback = []
        for result in validation_results:
            if result["score"] < 0.7:
                feedback.append(f"{result['rule'].title()}: {', '.join(result['feedback'])}")
        return "; ".join(feedback) if feedback else "All validations passed" 

    def validate_feature(self, feature: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Validate a feature against all rules"""
        results = []
        results.append(self._check_completeness(feature, context))
        # Add other validation checks here
        
        self.publish("validation_complete", {
            "type": "validation_complete",
            "data": {
                "feature": feature,
                "validation_results": results
            }
        }) 