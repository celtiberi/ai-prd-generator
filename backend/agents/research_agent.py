from typing import Dict, Any, Optional
import asyncio
from .base_agent import BaseAgent
from tavily import TavilyClient
from os import getenv
import uuid

class ResearchAgent(BaseAgent):
    def __init__(self, tavily_client=None):
        super().__init__("ResearchAgent")
        self.tavily_client = tavily_client or TavilyClient(api_key=getenv("TAVILY_API_KEY"))

    async def handle_event(self, event):
        """Handle incoming events"""
        if event["type"] == "research_request":
            result = await self.execute_task(event["data"])
            if result["status"] == "success":
                self.publish("research_complete", result["data"])

    async def execute_task(self, task: Dict[str, Any]):
        """Execute a research task"""
        try:
            # Search using Tavily
            results = await self._search_tavily(task["query"])
            
            # Process and store results
            processed_results = self._process_results(results)
            
            result = {
                "status": "success",
                "data": {
                    "task_id": task.get("task_id", str(uuid.uuid4())),
                    "query": task["query"],
                    "results": processed_results
                }
            }
            
            # Publish the result
            self.publish("research_complete", result["data"])
            
            return result
            
        except Exception as e:
            print(f"Research error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _search_tavily(self, query: str) -> Dict[str, Any]:
        """Perform search using Tavily API"""
        try:
            response = await self.tavily_client.search(query)
            return response
        except Exception as e:
            print(f"Tavily search error: {str(e)}")
            return {"error": str(e)}

    def _process_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Process and format search results"""
        if "error" in results:
            return {"error": results["error"]}
            
        processed = {
            "findings": [],
            "sources": []
        }
        
        for result in results.get("results", []):
            if result["relevance_score"] >= 0.7:
                processed["findings"].append({
                    "text": result["snippet"],
                    "source": result["url"],
                    "relevance": result["relevance_score"]
                })
                processed["sources"].append(result["url"])
                
        return processed 