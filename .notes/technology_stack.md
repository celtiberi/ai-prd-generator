# Technology Stack

This document defines the libraries, frameworks, and tools used in the project. Structure is provided in YAML format for AI parsing.

```yaml
technology_stack:
  documentation_location:
    path: .notes/dependencies
    structure:
      - {library_name}/
        - overview.md
        - usage.md
        - examples.md
        - integration.md
        - {library_name}_documentation.txt  # Official documentation
  
  core_dependencies:
    event_system:
      library: pypubsub
      version: "^4.0.3"
      purpose: Event-driven communication
      documentation:
        path: .notes/dependencies/pypubsub/pypubsub_documentation.txt
        format: text
      usage:
        - Inter-agent messaging
        - State change notifications
        - System events
    
    llm_integration:
      library: openai
      version: "^1.5.0"
      purpose: AI model interaction
      documentation:
        path: .notes/dependencies/openai/openai_documentation.md
        format: markdown
        key_sections:
          - Chat Completions API
          - Error handling
          - Rate limiting
          - Model usage
      usage:
        - Agent intelligence
        - Content generation
        - Analysis tasks
    
    vector_store:
      library: faiss-cpu
      version: "^1.7.4"
      purpose: Semantic search and storage
      usage:
        - Context storage
        - Similarity search
        - Memory persistence
    
    state_management:
      library: pydantic
      version: "^2.0.0"
      purpose: Data validation and state management
      usage:
        - State definitions
        - Data validation
        - Configuration management
    
    api_framework:
      library: fastapi
      version: "^0.100.0"
      purpose: API endpoints
      usage:
        - HTTP interface
        - Request handling
        - API documentation
    
    testing_framework:
      primary:
        library: pytest
        version: "^7.0.0"
        purpose: Testing infrastructure
      async_support:
        library: pytest-asyncio
        version: "^0.21.0"
        purpose: Async test support
    
    documentation:
      markdown:
        library: markdown
        version: "^3.4.0"
        purpose: Markdown processing
      yaml:
        library: pyyaml
        version: "^6.0.0"
        purpose: YAML processing

  development_tools:
    type_checking:
      library: mypy
      version: "^1.0.0"
      purpose: Static type checking
    
    linting:
      library: ruff
      version: "^0.1.0"
      purpose: Code quality enforcement
    
    formatting:
      library: black
      version: "^23.0.0"
      purpose: Code formatting

  version_constraints:
    python: ">=3.10,<4.0"
    node: ">=18.0.0"

  dependency_management:
    backend:
      tool: poetry
      files:
        - pyproject.toml
        - poetry.lock
    frontend:
      tool: yarn
      files:
        - package.json
        - yarn.lock

  event_bus:
    library: pypubsub
    version: "^4.0.3"
    features:
      - Topic-based routing ✓
      - Error handling ✓
      - Async support ✓
      - Event history ✓
      - Event filtering ✓
      implementation_status: completed
      notes:
        - In-memory event storage with size limits
        - Support for filtering and metrics
        - Integrated with system error handling
```

## Quick Reference

1. **Core Libraries**
   - Event System: `pypubsub`
   - LLM Integration: `openai`
   - Vector Store: `faiss-cpu`
   - State Management: `pydantic`
   - API Framework: `fastapi`

2. **Testing Tools**
   - Primary: `pytest`
   - Async Support: `pytest-asyncio`
   - Coverage: `pytest-cov`

3. **Development Tools**
   - Type Checking: `mypy`
   - Linting: `ruff`
   - Formatting: `black`

## Usage Guidelines

1. **Version Management**
   - Use specified versions in requirements
   - Test compatibility before updates
   - Document breaking changes

2. **Integration Patterns**
   - Follow library-specific best practices
   - Use provided type hints
   - Implement proper error handling 