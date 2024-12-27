
# Project Requirements Document (PRD)  
**Project:** Automated AI PRD Generation System  
**Version:** 1.8  
**Prepared for:** Cursor AI IDE  
**Date:** 2024-12-27  

---

## 1. Overview and Purpose  
The Automated AI PRD Generation System is designed to autonomously create structured Product Requirements Documents (`project.prd.md`) through multi-agent collaboration. This system will feature:  
- A **backend** for orchestrating AI agents that perform research, feature definition, and validation.  
- A **frontend** for user interaction, allowing iterative refinement of project goals.  
- **Local memory management** using FAISS and SQLite to ensure offline, cloud-independent operation.  

Cursor AI IDE will consume the final PRD to kickstart project development.  

---

## 2. Objectives  
- Automate PRD generation using a structured **multi-agent hierarchy**.  
- Enable **iterative feedback** loops between the user and the Lead Agent.  
- Store research data, dependencies, and project constraints locally using **FAISS** (vector) and **SQLite** (structured).  
- Facilitate **PRD visualization and download** through a React-based frontend.  

---

## 3. System Architecture  

### 3.1 High-Level Components  

1. **Backend (Multi-Agent System):**  
   - Modular system that delegates tasks to specialized agents.  
2. **Frontend (React Dashboard):**  
   - Provides a simple interface for project monitoring and user feedback.  
3. **Memory Management:**  
   - **FAISS** for embeddings (semantic search).  
   - **SQLite** for PRD metadata and dependencies.  

---

### 3.2 Agent Hierarchy and Class Structure  

**1. Lead Agent (Coordinator):**  
   - Orchestrates the entire workflow, interacts with the user, and delegates tasks to sub-agents.  
   - Manages iterative refinement of project goals.  

**2. Feature Definition Agents (Architects):**  
   - Translate high-level project goals into detailed features and use cases.  
   - Collaborate with Research Agents to gather technical information.  

**3. Research Agents (Scouts):**  
   - Query Tavily API to gather technical documentation and specifications.  
   - Store relevant data through the Memory Agent.  

**4. Validation Agents (Testers):**  
   - Validate PRD sections for completeness, identify missing dependencies, and interact with Feature Agents for refinements.  

**5. Memory Agent (Historian):**  
   - Stores and organizes data in FAISS and SQLite.  
   - Notifies other agents (`memory_updated`) when relevant data is available.  


#### Overview  
The Memory Agent plays a critical role in maintaining **long-term project memory** by storing and organizing data collected by other agents. It uses a combination of **FAISS** for vector-based embeddings and **SQLite** for structured relational data.  
This agent passively records incoming data and **broadcasts notifications** (`memory_updated`) but does not directly supply data to other agents. Agents query the databases directly as needed.  

---

#### Responsibilities  
- **Data Storage:** Stores technical documentation, project features, dependencies, and embeddings.  
- **Event Listening:** Listens for `update_memory` events to archive data received from Research and Feature Agents.  
- **Notification:** Publishes `memory_updated` events when new data is stored, informing agents of available information.  
- **Query Independence:** Agents access long-term memory by querying FAISS or SQLite directly, promoting loose coupling.  

---

#### Memory Architecture  
| Component              | Description                                     |  
|-----------------------|-------------------------------------------------|  
| **Vector Database**    | **FAISS** - Stores embeddings of documents and PRD sections. Enables fast semantic search. |  
| **Structured Database**| **SQLite** - Stores feature metadata, dependencies, and constraints.                   |  

---

#### How It Works  

1. **Event-Driven Storage:**  
   - When agents collect data (e.g., research results), they publish an `update_memory` event.  
   - The Memory Agent processes the event, stores the data, and triggers `memory_updated` to notify the system.  

2. **Long-Term Data Retrieval:**  
   - Agents querying past data interact directly with FAISS (vector search) or SQLite (SQL queries).  
   - The Memory Agent is **not responsible for serving data** but ensures it is **available and organized**.  

---

#### Example Implementation  

```python
import faiss
import sqlite3

# Memory Agent Class
class MemoryAgent:
    def __init__(self, event_bus):
        self.vector_db = faiss.IndexFlatL2(768)  # Example FAISS index
        self.sql_db = sqlite3.connect("db/prd_database.db")
        self.event_bus = event_bus
        event_bus.subscribe("update_memory", self.handle_event)

    def handle_event(self, event):
        if event['type'] == 'update_memory':
            self.store(event['data'])

    def store(self, data):
        # Store embeddings in FAISS
        embedding = self.generate_embedding(data['text'])
        self.vector_db.add(embedding)

        # Store metadata in SQLite
        cursor = self.sql_db.cursor()
        cursor.execute("INSERT INTO features (name, description, status) VALUES (?, ?, ?)",
                       (data['name'], data['text'], 'active'))
        self.sql_db.commit()

        # Notify agents of memory update
        self.event_bus.put({'type': 'memory_updated', 'data': data})

    def generate_embedding(self, text):
        # Simulate text embedding (replace with actual model call)
        return faiss.vector_to_array([float(ord(c)) for c in text[:768]])

```python
# Base Agent (Shared Methods)
class BaseAgent:
    def __init__(self, name, event_bus):
        self.name = name
        self.event_bus = event_bus
        self.log(f"{self.name} initialized")

    def log(self, message):
        print(f"[{self.name}] {message}")

    def subscribe(self, event_type):
        self.event_bus.subscribe(event_type, self.handle_event)

    def publish(self, event_type, data):
        self.event_bus.publish(event_type, data)

    def handle_event(self, event):
        raise NotImplementedError("Override required")

    def execute_task(self, task):
        raise NotImplementedError("Override required")
```

## 3.3 Agent Communication (Event Bus)

### Overview  
The agents communicate through an **in-memory event bus** implemented using Python’s `queue.Queue`. This approach facilitates asynchronous, decoupled message passing between agents, enabling efficient task distribution and coordination.  

### Key Concepts  
- **Event-Driven Architecture:** Agents publish and subscribe to events (tasks, research results, etc.).  
- **Loose Coupling:** Agents do not directly call each other but rely on the event bus to handle communication.  
- **Scalability:** The queue handles multiple tasks without blocking, allowing parallel processing by different agents.  

### Implementation Example  

```python
import queue
import threading

# Global event bus (shared queue)
event_bus = queue.Queue()

# Base Agent Class
class BaseAgent:
    def __init__(self, name):
        self.name = name
        threading.Thread(target=self.listen_for_events).start()

    def listen_for_events(self):
        while True:
            event = event_bus.get()
            if event['target'] == self.name:
                self.handle_event(event)

    def publish(self, event_type, data, target):
        event_bus.put({'type': event_type, 'data': data, 'target': target})

    def handle_event(self, event):
        raise NotImplementedError("Override this method to handle events")

# Example: Lead Agent
class LeadAgent(BaseAgent):
    def handle_event(self, event):
        print(f"[{self.name}] Handling event: {event}")

# Example: Research Agent
class ResearchAgent(BaseAgent):
    def handle_event(self, event):
        print(f"[{self.name}] Performing research for: {event['data']}")
        self.publish('research_done', {'result': 'Tech doc found'}, 'LeadAgent')

# Initialize Agents
lead_agent = LeadAgent("LeadAgent")
research_agent = ResearchAgent("ResearchAgent")

# Publish Event
event_bus.put({'type': 'research_request', 'data': 'OAuth best practices', 'target': 'ResearchAgent'})
```

### Benefits  
- **Modularity:** Agents can be added or removed without affecting existing workflows.  
- **Asynchronous Execution:** Agents operate independently, processing tasks in parallel.  
- **Simplified Communication:** Centralized queue prevents the need for complex inter-agent dependencies. 
---

---

## 4. Tech Stack  

## 4.1 Backend  

| Component           | Description                                   |  
|--------------------|-----------------------------------------------|  
| **Language**        | Python                                        |  
| **API Framework**   | FastAPI / Flask                               |  
| **Vector Database** | FAISS (local embedding storage)               |  
| **SQL Database**    | SQLite (local structured data)                |  
| **AI Models**       | OpenAI API (GPT)                              |  
| **Research API**    | Tavily API                                    |  
| **Event Bus**       | Python’s `queue.Queue` (in-memory messaging)  |  

## 4.2 Frontend  

| Component           | Description                                   |  
|--------------------|-----------------------------------------------|  
| **Language**        | JavaScript / TypeScript                       |  
| **Framework**       | React                                         |  
| **State Management**| React Context / Zustand                       |  
| **API Communication** | Axios / Fetch                               |  
| **Styling**         | Tailwind CSS or Bootstrap                    |  


## 5. File Structure  

```
/ai-prd-generator  
│  
├── backend  
│   ├── agents  
│   │   ├── lead_agent.py  
│   │   ├── research_agent.py  
│   │   ├── feature_agent.py  
│   │   ├── validation_agent.py  
│   │   └── memory_agent.py  
│   ├── db  
│   │   ├── faiss_index/  
│   │   └── schema.sql  
│   ├── api  
│   │   └── routes.py  
│   ├── events  
│   │   └── event_bus.py  
│  
├── frontend  
│   ├── src  
│   │   ├── components  
│   │   └── App.tsx  
│  
├── config  
│   ├── .env  
│   └── settings.py  
└── README.md  
```  

---

## 6. API Routes  

- **`POST /api/init`** – Initialize PRD generation.  
- **`POST /api/feedback`** – Submit feedback to refine PRD.  
- **`GET /api/progress`** – Retrieve PRD progress.  
- **`GET /api/download`** – Download the PRD.  

---

## 7. Database Design  

```sql
CREATE TABLE features (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    status TEXT
);
CREATE TABLE dependencies (
    id INTEGER PRIMARY KEY,
    feature_id INTEGER,
    description TEXT,
    FOREIGN KEY(feature_id) REFERENCES features(id)
);
```

---

## 8. Workflow Diagram  

```
[User Input]  
     |  
[Lead Agent]   
     |  
     |---> [Feature Agents]  
               |  
               |---> [Research Agents]  
               |         |  
               |         |---> [Tavily API / Docs]  
               |         |  
               |         +---> [Memory Agent (Store Data)]  
               |  
               |---> [Validation Agents]  
                          |  
                          +---> [Feature Agents (Rework)]  
     |  
[Lead Agent (Compile PRD)]  
     |  
     |---> [Frontend Download / Database Storage]  
```
