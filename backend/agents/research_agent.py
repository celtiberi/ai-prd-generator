from typing import Dict, Any, List
import aiohttp
import asyncio
from .base_agent import BaseAgent

class ResearchAgent(BaseAgent):
    def __init__(self, event_bus, api_key: str):
        super().__init__("ResearchAgent", event_bus)
        self.api_key = api_key
        self.active_searches: Dict[str, Any] = {}
        
        # Subscribe to research requests
        self.subscribe("research_request")

    async def _search_tavily(self, query: str) -> Dict:
        """Perform research using Tavily API"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "X-API-KEY": self.api_key,
                "content-type": "application/json"
            }
            payload = {
                "query": query,
                "search_depth": "advanced",
                "include_domains": ["github.com", "stackoverflow.com", "medium.com"],
                "max_results": 5
            }
            
            async with session.post(
                "https://api.tavily.com/search",
                headers=headers,
                json=payload
            ) as response:
                return await response.json()

    def handle_event(self, event):
        """Handle research requests"""
        if event.type == "research_request":
            self.execute_task(event.data)

    def execute_task(self, task: Dict):
        """Execute a research task"""
        # Create asyncio event loop and run search
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(self._search_tavily(task["query"]))
            self._process_results(task, results)
        finally:
            loop.close()

    def _process_results(self, task: Dict, results: Dict):
        """Process and summarize research results"""
        processed_results = {
            "task_id": task["task_id"],
            "query": task["query"],
            "results": self._summarize_results(results),
            "context": task["context"]
        }
        
        # Publish research results
        self.publish("research_complete", processed_results, target="LeadAgent")

    def _summarize_results(self, results: Dict) -> Dict:
        """Summarize the research results"""
        summary = {
            "main_findings": [],
            "sources": []
        }
        
        if "results" in results:
            for result in results["results"]:
                summary["sources"].append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("snippet", "")
                })
                
                if result.get("relevance_score", 0) > 0.7:
                    summary["main_findings"].append(result.get("snippet", ""))

        return summary 