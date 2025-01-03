# Component Architecture

This document describes the relationships and interactions between major components. Structure is provided in YAML format for AI parsing.

```yaml
architecture:
  agent_system:
    description: Multi-agent system for PRD generation
    components:
      lead_agent:
        role: Orchestration and coordination
        dependencies: [all other agents]
        key_responsibilities:
          - Receive project summary from consultant
          - Coordinate feature definition process
          - Manage agent interactions
          - Generate final documentation
          - Maintain project consistency
      project_consultant_agent:
        role: Initial project understanding
        dependencies: [llm_service]
        key_responsibilities:
          - Interactive user consultation
          - Requirements gathering
          - Project scope definition
          - Generate comprehensive summary
          - Pass summary to lead agent
      research_agent:
        role: Information gathering
        dependencies: [llm_service, memory_agent]
        key_responsibilities:
          - Support feature agents with research
          - Find relevant technical information
          - Identify implementation patterns
          - Cache research results
      feature_agent:
        role: Feature definition and refinement
        dependencies: [research_agent, validation_agent]
        key_responsibilities:
          - Analyze feature requirements
          - Collaborate with research agent
          - Define detailed specifications
          - Iterate with validation agent
          - Return completed features to lead agent
      validation_agent:
        role: Feature validation and quality assurance
        dependencies: [feature_agent]
        key_responsibilities:
          - Validate feature specifications
          - Check against project requirements
          - Provide feedback to feature agents
          - Ensure feature completeness
          - Validate documentation completeness
          - Ensure documentation detail requirements
          documentation_validation:
            - Check for required sections
            - Validate cross-references
            - Verify schema compliance
            - Ensure implementation details
            - Validate event specifications
      memory_agent:
        role: Persistent storage
        dependencies: [vector_store, sqlite]
        key_responsibilities:
          - Store conversation history
          - Maintain project context
          - Enable semantic search
      
      workflows:
        project_initialization:
          steps:
            - User interacts with project consultant
            - Consultant generates project summary
            - Summary passed to lead agent
            - Lead agent plans feature breakdown
        
        feature_development:
          steps:
            - Lead agent assigns features to feature agents
            - Feature agents request research support
            - Research agent provides information
            - Feature agents define specifications
            - Validation agent reviews features
            - Features iterate until validated
            - Completed features return to lead agent
        
        documentation_generation:
          steps:
            - Lead agent collects all validated features
            - Generates structured documentation
            - Creates cross-referenced markdown files
            - Maintains YAML compatibility
            - Generates testing requirements
        
        documentation_outputs:
          core_docs:
            - project.prd.md: Project overview and structure
            - component_architecture.md: System design and interactions
            - development_guidelines.md: Development standards
            - implementation_strategy.md: Build order and dependencies
          
          technical_docs:
            - schemas.md: Data structure definitions
            - events.md: Event system specifications
            - api.md: External integrations
          
          quality_docs:
            - testing_guidelines.md:
                purpose: Ensure system quality and reliability
                includes:
                  - Testing strategy
                  - Agent test specifications
                  - Mock requirements
                  - CI/CD configuration
```

## Component Interaction Flow

1. **Project Initialization**
   ```mermaid
   sequenceDiagram
       User->>ProjectConsultant: Project Requirements
       ProjectConsultant->>LLMService: Process Requirements
       ProjectConsultant->>LeadAgent: Project Summary
       LeadAgent->>FeatureAgent: Feature Assignments
   ```

2. **Feature Development**
   ```mermaid
   sequenceDiagram
       FeatureAgent->>ResearchAgent: Research Request
       ResearchAgent-->>FeatureAgent: Research Results
       FeatureAgent->>ValidationAgent: Feature Spec
       ValidationAgent-->>FeatureAgent: Validation Feedback
       loop Until Validated
           FeatureAgent->>ValidationAgent: Updated Spec
           ValidationAgent-->>FeatureAgent: Feedback
       end
       FeatureAgent->>LeadAgent: Validated Feature
   ```

3. **Documentation Generation**
   ```mermaid
   sequenceDiagram
       LeadAgent->>LeadAgent: Collect Features
       LeadAgent->>Documentation: Generate project.prd.md
       LeadAgent->>Documentation: Generate component_architecture.md
       LeadAgent->>Documentation: Generate other docs
       Documentation-->>User: Complete Documentation Set
   ``` 