from typing import Dict, Any
from .base_agent import BaseAgent
from ..services.llm_service import LLMService
import json

# Define feature analysis schema
FEATURE_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "requirements": {
            "type": "array",
            "items": {"type": "string"}
        },
        "priority": {
            "type": "string",
            "enum": ["high", "medium", "low"]
        },
        "dependencies": {
            "type": "array",
            "items": {"type": "string"}
        },
        "implementation_details": {"type": "string"}
    },
    "required": ["name", "description", "requirements", "priority"]
}

class FeatureAgent(BaseAgent):
    def __init__(self, llm_service=None):
        super().__init__("FeatureAgent")
        self.llm = llm_service or LLMService()

    async def handle_event(self, event: Dict[str, Any]) -> None:
        """Handle incoming feature requests"""
        if event["type"] == "feature_request":
            feature = event["data"]["feature"]
            context = event["data"]["context"]
            
            result = await self.analyze_feature(feature, context)
            
            self.publish("feature_defined", {
                "type": "feature_defined",
                "data": {
                    "feature": result,
                    "context": context
                }
            })

    async def analyze_feature(self, feature: Dict[str, Any], context: Dict[str, Any]):
        """Analyze and expand a feature definition"""
        try:
            response = await self.llm.structured_output(
                messages=[{
                    "role": "user",
                    "content": f"Analyze this feature in context:\nFeature: {json.dumps(feature)}\nContext: {json.dumps(context)}"
                }],
                output_schema=FEATURE_SCHEMA
            )
            
            if response["status"] == "success":
                # Publish the feature_defined event
                self.publish("feature_defined", {
                    "feature": response["data"]
                })
                
                return {
                    "status": "success",
                    "data": response["data"]
                }
            else:
                return {
                    "status": "error",
                    "error": response.get("error", "Unknown error")
                }
                
        except Exception as e:
            print(f"Feature analysis error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            } 