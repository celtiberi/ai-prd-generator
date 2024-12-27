from queue import Queue
from typing import Dict, List, Callable
import threading
from dataclasses import dataclass
from typing import Any

@dataclass
class Event:
    type: str
    data: Any
    target: str = None

class EventBus:
    def __init__(self):
        self._queue = Queue()
        self._subscribers: Dict[str, List[Callable]] = {}
        self._running = True
        self._start_processing()

    def _start_processing(self):
        def process_events():
            while self._running:
                try:
                    event = self._queue.get(timeout=1.0)  # 1 second timeout
                    self._process_event(event)
                except Queue.Empty:
                    continue

        thread = threading.Thread(target=process_events, daemon=True)
        thread.start()

    def _process_event(self, event: Event):
        if event.type in self._subscribers:
            for callback in self._subscribers[event.type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error processing event {event.type}: {str(e)}")

    def publish(self, event_type: str, data: Any, target: str = None):
        event = Event(type=event_type, data=data, target=target)
        self._queue.put(event)

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def shutdown(self):
        self._running = False 