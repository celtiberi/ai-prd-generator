from typing import Dict, Any, List
from .base_agent import BaseAgent
from services.llm_service import LLMService
from schemas.project_schemas import PROJECT_SUMMARY_SCHEMA, validate_project_summary

class ProjectConsultantAgent(BaseAgent):
    def __init__(self):
        super().__init__("ProjectConsultantAgent")
        self.conversation_history = []
        self.current_summary = None
        self.llm = LLMService()
        
        self.system_prompt = """You are an experienced product consultant helping users define their software projects. 
        Guide the conversation to understand:
        1. The core problem/need
        2. Target users and their pain points
        3. Key goals and success metrics
        4. Potential features and priorities
        
        Ask focused questions one at a time. Be encouraging but also probe for important details."""

    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process user message and guide the conversation"""
        try:
            self.conversation_history.append({"role": "user", "content": message})
            
            if self._is_ready_for_summary():
                return await self._generate_structured_summary()
            
            response = await self.llm.chat_completion(self.conversation_history)
            if response["status"] == "success":
                self.conversation_history.append({"role": "assistant", "content": response["content"]})
                return {
                    "message": response["content"],
                    "status": "consulting"
                }
            
            return {
                "message": f"Error: {response.get('error', 'Unknown error')}",
                "status": "error"
            }
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            return {
                "message": f"Error: {str(e)}",
                "status": "error"
            }

    def _is_ready_for_summary(self) -> bool:
        """Check if we have enough information for a summary"""
        required_topics = ["problem", "users", "goals", "features"]
        conversation_text = " ".join(msg["content"].lower() 
                                   for msg in self.conversation_history)
        return all(topic in conversation_text for topic in required_topics)

    async def _generate_structured_summary(self) -> Dict[str, Any]:
        """Generate structured summary from conversation"""
        messages = [
            {
                "role": "system",
                "content": """Based on the conversation, generate a structured project summary.
                Extract key information and organize it into a clear, structured format."""
            },
            {
                "role": "user",
                "content": f"Generate a structured summary from this conversation: {self.conversation_history}"
            }
        ]

        response = await self.llm.structured_output(messages, PROJECT_SUMMARY_SCHEMA)
        if response["status"] == "success" and validate_project_summary(response["data"]):
            self.current_summary = response["data"]
            return {
                "message": "I've prepared a structured summary of your project. Please review:",
                "summary": self.current_summary,
                "status": "review_summary"
            }
        
        return {"message": "Error generating summary", "status": "error"}

    def approve_summary(self) -> Dict[str, Any]:
        """Finalize the summary and notify LeadAgent"""
        if not self.current_summary:
            raise ValueError("No summary to approve")
            
        self.publish("project_summary_ready", self.current_summary)
        
        return {
            "status": "summary_approved",
            "message": "Great! I'm passing this to our lead agent for detailed analysis."
        } 