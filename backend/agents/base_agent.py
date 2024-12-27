from typing import Any
from ..events.event_bus import EventBus

class BaseAgent:
    def __init__(self, name: str, event_bus: EventBus):
        self.name = name
        self.event_bus = event_bus
        self.log(f"{self.name} initialized")

    def log(self, message: str):
        print(f"[{self.name}] {message}")

    def subscribe(self, event_type: str):
        self.event_bus.subscribe(event_type, self.handle_event)

    def publish(self, event_type: str, data: Any, target: str = None):
        self.event_bus.publish(event_type, data, target)

    def handle_event(self, event):
        """Override this method in derived agent classes"""
        raise NotImplementedError("handle_event must be implemented by derived classes")

    def execute_task(self, task: Any):
        """Override this method in derived agent classes"""
        raise NotImplementedError("execute_task must be implemented by derived classes") 