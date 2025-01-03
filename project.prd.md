# AI PRD Generator

## Architecture

### Core Components

1. **LLM Service**
   - Centralized service for all AI/LLM interactions
   - Currently uses OpenAI's GPT-4
   - Abstracted interface for potential future LLM changes
   - Handles structured output parsing
   - Manages API key and rate limiting

2. **Agents**
   - All agents use LLM service for intelligent processing
   - **Project Consultant Agent**: Guides initial project definition
   - **Lead Agent**: Coordinates PRD generation
   - **Research Agent**: Gathers relevant information
   - **Feature Agent**: Defines detailed features
   - **Validation Agent**: Ensures quality and completeness
