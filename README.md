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

- Python 3.13+
- Node.js 18+
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
cd backend
pip install -r requirements.txt
cd ..
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
│   ├── main.py
│   └── requirements.txt
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

## Development Requirements

- Python 3.9-3.11 (Python 3.12 is not yet supported due to faiss-cpu compatibility) 

## Development Best Practices

### AI-Human Collaborative Development

This project uses a collaborative workflow between human developers and AI assistants:

1. **Documentation First**
   - AI analyzes `.notes/*.md` files for requirements
   - Human provides external dependency docs in `.notes/dependencies/`
   - Both review requirements and identify gaps
   - Example from LLM service:
     ```
     AI: Reviews api.md, technology_stack.md
     Human: Provides OpenAI SDK docs in .notes/dependencies/
     AI: Identifies missing rate limiting details
     Both: Agree on token bucket algorithm implementation
     ```

2. **Iterative Implementation**
   - AI proposes initial implementation
   - Human runs tests and provides feedback
   - AI analyzes test failures and logs
   - Both iterate on fixes
   - Example from event system:
     ```
     AI: Implements event system with PyPubSub
     Human: Runs tests, shows validation errors
     AI: Analyzes logs, fixes event type validation
     Human: Tests again, shows filtering issues
     AI: Implements custom filtering solution
     ```

3. **Test-Driven Refinement**
   - Human provides test output and logs
   - AI diagnoses issues from error messages
   - Both discuss test requirements
   - Example from both implementations:
     ```
     Human: Shows test failures with stack traces
     AI: Identifies issues (e.g., Mock object structure)
     Human: Confirms fixes with new test runs
     AI: Suggests additional test cases
     ```

4. **Documentation Updates**
   - AI updates implementation status
   - AI adds implementation notes and patterns
   - Human reviews documentation accuracy
   - Example from completed features:
     ```
     AI: Marks component as completed
     AI: Documents key patterns (e.g., token bucket, event filtering)
     Human: Reviews implementation notes
     AI: Updates changelog and tech stack docs
     ```

### Key Success Patterns

Our implementations have revealed several effective patterns:

1. **Incremental Complexity**
   - Start with core functionality
   - Add advanced features iteratively
   - Test each addition thoroughly

2. **Error-Driven Development**
   - Use test failures as guidance
   - Analyze error messages carefully
   - Fix one issue at a time

3. **Documentation Synchronization**
   - Keep .notes files updated
   - Document learned patterns
   - Maintain changelog

### Component Implementation Flow

1. **Documentation First**
   - Review relevant `.notes/*.md` files for requirements
   - Ensure external dependency documentation exists in `.notes/dependencies/`
   - Example: For event system, needed:
     - `.notes/events.md`
     - `.notes/dependencies/pypubsub/pypubsub_documentation.txt`

2. **Implementation**
   - Create component implementation
   - Create corresponding test file
   - Follow patterns from documentation
   - Example: For event system:
     ```
     backend/core/event_system.py
     backend/tests/core/test_event_system.py
     ```

3. **Test-Driven Refinement**
   - Run tests with detailed logging
     ```bash
     pytest -s --log-cli-level=DEBUG path/to/test.py
     ```
   - Debug and fix issues
   - Iterate until tests pass

4. **Documentation Updates**
   - Update relevant documentation with learnings
   - Document discovered patterns and requirements
   - Example: Updated `.notes/events.md` with:
     - Topic naming conventions
     - Handler signature requirements
     - Error handling patterns

### Key Principles

1. **Documentation Driven**
   - Start with comprehensive documentation
   - Keep documentation in sync with implementation
   - Document external dependency usage

2. **Test First**
   - Create tests alongside implementation
   - Use tests to validate documentation accuracy
   - Detailed logging for debugging

3. **Iterative Refinement**
   - Implement core functionality
   - Test and debug
   - Update documentation
   - Repeat until complete

4. **External Dependencies**
   - Store official documentation in `.notes/dependencies/`
   - Reference documentation in implementation
   - Update our docs based on learned patterns 

### Real Implementation Example: LLM Service

The LLM service implementation demonstrates our workflow:

1. **Documentation First**
   - Started with requirements in `api.md` and `technology_stack.md`
   - Referenced OpenAI SDK docs in `.notes/dependencies/`
   - Identified core features: chat completion, embeddings, rate limiting

2. **Iterative Implementation**
   - Basic OpenAI integration
   - Added token bucket rate limiting
   - Implemented function calling and streaming
   - Added proper error handling and event system integration

3. **Test-Driven Development**
   - Created tests for each feature
   - Fixed mock objects to match OpenAI response format
   - Added cleanup between tests
   - Achieved full test coverage

4. **Documentation Updates**
   - Marked component as completed
   - Added implementation notes
   - Documented key patterns for future reference
   - Maintained immutable external dependency docs 