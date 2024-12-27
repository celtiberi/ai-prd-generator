# AI PRD Generator

An intelligent system that automatically generates and refines Product Requirements Documents (PRDs) using a multi-agent architecture and AI-powered research.

## 🌟 Features

- **Automated PRD Generation**: Convert high-level objectives into detailed feature specifications
- **Intelligent Research**: Automatically research and incorporate best practices and industry standards
- **Feature Validation**: Validate features for completeness, consistency, and feasibility
- **Interactive Refinement**: Get feedback and refine features iteratively
- **Memory Management**: Efficient storage and retrieval of research findings and feature specifications
- **Real-time Progress Tracking**: Monitor PRD generation progress through a modern web interface

## 🏗️ Architecture

The system uses a multi-agent architecture:

- **Lead Agent**: Coordinates the overall PRD generation process
- **Research Agent**: Performs intelligent research using the Tavily API
- **Feature Agent**: Converts research and objectives into detailed features
- **Validation Agent**: Ensures feature quality and feasibility
- **Memory Agent**: Manages persistent storage and retrieval

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- SQLite3
- Yarn

### Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-prd-generator.git
cd ai-prd-generator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install backend dependencies:
```bash
pip install -r requirements.txt
```

4. Install frontend dependencies:
```bash
cd frontend
yarn install
```

5. Create a `.env` file in the config directory:
```env
# Server Settings
API_PORT=5000
DEBUG_MODE=True
HOST=0.0.0.0

# Agent Settings
AGENT_TIMEOUT=300
RESEARCH_AGENT_THREADS=5

# API Keys
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key

# Database Settings
FAISS_INDEX_PATH=./db/faiss_index
SQLITE_DB_PATH=./db/prd_database.db

# Vector Settings
VECTOR_DIM=768
```

### Running the Application

1. Start the backend server:
```bash
cd backend
python main.py
```

2. Start the frontend development server:
```bash
cd frontend
yarn dev
```

The application will be available at `http://localhost:3000`

## 🧪 Running Tests

### Backend Tests

Run all tests:
```bash
pytest backend/tests
```

Run specific test categories:
```bash
pytest backend/tests/agents  # Test agents
pytest backend/tests/events  # Test event system
pytest backend/tests/test_integration.py  # Run integration tests
```

Run tests with coverage:
```bash
pytest --cov=backend tests/
```

### Frontend Tests

```bash
cd frontend
yarn test
```

## 📁 Project Structure

```
ai-prd-generator/
├── backend/
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── lead_agent.py
│   │   ├── research_agent.py
│   │   ├── feature_agent.py
│   │   ├── validation_agent.py
│   │   └── memory_agent.py
│   ├── api/
│   │   └── routes.py
│   ├── events/
│   │   └── event_bus.py
│   ├── tests/
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── types/
│   └── package.json
├── config/
│   ├── settings.py
│   └── .env
└── requirements.txt
```

## 🔄 API Endpoints

- `POST /api/init` - Initialize PRD generation
- `POST /api/feedback` - Submit feedback for PRD refinement
- `GET /api/progress` - Get current PRD generation progress
- `GET /api/download` - Download the generated PRD

## 🗄️ Database Schema

```sql
-- Features table
CREATE TABLE features (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'draft',
    priority TEXT,
    requirements TEXT,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dependencies table
CREATE TABLE dependencies (
    id INTEGER PRIMARY KEY,
    feature_id INTEGER,
    description TEXT,
    type TEXT,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY(feature_id) REFERENCES features(id)
);
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Tavily API](https://tavily.com) for research capabilities
- [OpenAI](https://openai.com) for language models
- [FastAPI](https://fastapi.tiangolo.com) for the backend framework
- [React](https://reactjs.org) and [Chakra UI](https://chakra-ui.com) for the frontend 