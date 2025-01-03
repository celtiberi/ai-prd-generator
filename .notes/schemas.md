# Schema Documentation

This document defines the data structures and validation rules used throughout the project. All schemas are provided in YAML format for AI parsing.

```yaml
schemas:
  project_summary:
    description: Initial project requirements and scope
    structure:
      title: string
      description: string
      objectives: string[]
      requirements:
        functional: string[]
        technical: string[]
      constraints: string[]
      
  feature:
    description: Individual feature specification
    structure:
      name: string
      description: string
      requirements: string[]
      dependencies: string[]
      priority:
        type: enum
        values: [high, medium, low]
      validation_status:
        type: enum
        values: [draft, in_review, validated, needs_revision]
        
  validation_feedback:
    description: Validation agent feedback format
    structure:
      feature_name: string
      status: enum[valid, invalid]
      feedback: string[]
      suggested_changes: string[]
      validation_score: float
      
  event_message:
    description: Inter-agent communication format
    structure:
      type: string
      source_agent: string
      target_agent: string
      timestamp: datetime
      payload: any
      correlation_id: string
      
  documentation_template:
    description: Base structure for generated documents
    structure:
      title: string
      description: string
      yaml_section:
        format: yaml
        required: true
      sections:
        - title: string
          content: string
          subsections: array
      validation_requirements:
        event_system:
          required_sections:
            - Subscription patterns with examples
            - Complete event type hierarchy
            - Payload requirements for each event
            - Event persistence strategy
            - Full subscription matrix
            - Error handling procedures
          validation_rules:
            - All events must have defined payloads
            - All agents must have publish/subscribe lists
            - Error handling must be specified for each event type
            - Persistence strategy must be defined 