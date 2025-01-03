from pubsub import pub
from typing import Any, Dict

class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.log(f"{self.name} initialized")

    def log(self, message: str):
        print(f"[{self.name}] {message}")

    def subscribe(self, event_type: str):
        pub.subscribe(self.handle_event, event_type)

    def publish(self, topic: str, data: Dict[str, Any]) -> None:
        """Publish an event to the event bus"""
        # Always wrap data in a standard event structure
        event = {
            "type": topic,
            "data": data
        }
        pub.sendMessage(topic, event=event)

    def handle_event(self, event):
        """Override this method in derived agent classes"""
        raise NotImplementedError("handle_event must be implemented by derived classes")

    def execute_task(self, task: Any):
        """Override this method in derived agent classes"""
        raise NotImplementedError("execute_task must be implemented by derived classes") 