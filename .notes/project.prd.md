# AI Project Documentation Generator

This document provides a high-level overview of the project, with detailed information available in referenced documents.

```yaml
project:
  name: AI Project Documentation Generator
  description: |
    A multi-agent system that collaboratively generates comprehensive project documentation,
    using AI to create maintainable, structured, and interconnected documentation sets.
  
  core_objectives:
    - Create complete, AI-parseable documentation suites
    - Generate structured project documentation through agent collaboration
    - Create maintainable, AI-parseable documentation using YAML
    - Ensure comprehensive coverage through specialized agents
    - Maintain consistency between interconnected documents
    - Enable continuous documentation updates
    
  agent_workflow:
    initialization:
      agent: project_consultant_agent
      purpose: Gather project requirements through user interaction
      output: Comprehensive project summary
    
    orchestration:
      agent: lead_agent
      purpose: Coordinate feature development and documentation
      responsibilities:
        - Distribute features to feature agents
        - Monitor validation process
        - Generate final documentation
        - Ensure documentation consistency
        - Maintain cross-references
    
    feature_development:
      agents: [feature_agent, research_agent, validation_agent]
      process:
        - Feature analysis and research
        - Specification development
        - Iterative validation
        - Final approval
        - Documentation integration
    
  documentation_approach:
    format: YAML-based markdown
    principles:
      - AI-parseable structure
      - Human readability
      - Cross-referenced documents
      - Version controlled
      - Automated updates
    organization:
      core_docs:
        - Project overview
        - Architecture design
        - Development standards
        - Implementation strategy
      technical_docs:
        - API specifications
        - Data schemas
        - Event systems
      dependency_docs:
        location: .notes/dependencies
        purpose: Integration documentation
        requirements:
          - Library usage patterns
          - Integration examples
          - Error handling
          - Best practices
        update_strategy:
          - Version change triggers
          - API updates
          - Breaking changes
      quality_docs:
        - Testing guidelines
        - Security standards
        - Error handling
    
  key_documents:
    implementation:
      file: .notes/implementation_strategy.md
      contains:
        - Implementation phases
        - Component dependencies
        - Build order
        - Testing approach
        - Development guidelines
    
    architecture:
      file: .notes/component_architecture.md
      contains:
        - Agent system design
        - Component relationships
        - Interaction flows
        - Workflow diagrams
        - Communication protocols
    
    development:
      file: .notes/development_guidelines.md
      contains:
        - Code standards
        - Git workflow
        - Error handling
        - Agent development patterns
    
    testing:
      file: .notes/testing_guidelines.md
      contains:
        - Testing strategy and principles
        - Test types and coverage targets
        - Agent-specific test requirements
        - Mock and fixture specifications
        - CI/CD integration requirements
        
    progress:
      file: .notes/changelog.md
      contains:
        - Version history
        - Current status
        - Planned features
        - Agent implementation status
    
    schemas:
      file: .notes/schemas.md
      contains:
        - Data structure definitions
        - Validation rules
        - Event message formats
        - Documentation templates
        - Schema versioning
    
    events:
      file: .notes/events.md
      contains:
        - Event types and payloads
        - Publisher/subscriber patterns
        - Event flow diagrams
        - Error handling patterns
    
    api:
      file: .notes/api.md
      contains:
        - External service integrations
        - Rate limiting strategies
        - Authentication handling
        - Response formats
    
    state:
      file: .notes/state_management.md
      contains:
        - Agent state transitions
        - Project context lifecycle
        - Memory persistence patterns
        - Event-driven state changes
    
    error_handling:
      file: .notes/error_handling.md
      contains:
        - Error types and hierarchies
        - Recovery strategies
        - Cross-agent error propagation
        - LLM error handling patterns
    
    prompts:
      file: .notes/prompts.md
      contains:
        - System prompts by agent
        - Prompt templates
        - Context management
        - Chain of thought patterns
    
    security:
      file: .notes/security.md
      contains:
        - API key management
        - Input validation
        - Data sanitization
        - Access controls
    
    technology:
      file: .notes/technology_stack.md
      contains:
        - Core dependencies
        - Development tools
        - Version constraints
        - Integration patterns

  status:
    current_phase: Project Setup
    next_milestone: Feature Implementation
    key_priorities:
      - Implement initial agent system
      - Establish documentation generation pipeline
      - Create agent collaboration framework
      - Set up validation and feedback loops
      - Develop documentation maintenance system
```

## Quick Links

- [Component Architecture](.notes/component_architecture.md)
- [Development Guidelines](.notes/development_guidelines.md)
- [Testing Guidelines](.notes/testing_guidelines.md)
- [Changelog](.notes/changelog.md)
- [State Management](.notes/state_management.md)
- [Security Guidelines](.notes/security.md)
- [API Documentation](.notes/api.md)
- [Event System](.notes/events.md)

## Implementation Notes

The system uses a multi-agent architecture where each agent has a specialized role in the documentation generation process. The workflow is designed to be:

1. **Interactive Requirements Gathering**
   - Project consultant agent works with users
   - Builds comprehensive project understanding
   - Generates structured project summary

2. **Feature Development Pipeline**
   - Lead agent coordinates feature development
   - Feature agents collaborate with research agents
   - Validation ensures quality and completeness

3. **Documentation Generation**
   - YAML-based structure for AI parsing
   - Cross-referenced documentation set
   - Maintained through git hooks
   - Continuous updates and validation
   - Version controlled documentation

4. **Documentation Maintenance**
   - Automated consistency checks
   - Cross-reference validation
   - Schema compliance verification
   - Documentation health monitoring 