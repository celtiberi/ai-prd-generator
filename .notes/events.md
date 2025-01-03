# Event System Documentation

This document defines the event-driven communication system used between agents. Structure is provided in YAML format for AI parsing.

```yaml
event_system:
  patterns:
    publisher_subscriber:
      description: Asynchronous event distribution
      implementation: pypubsub
      error_handling:
        strategy: retry_with_backoff
        parameters:
          initial_delay: 1.0  # seconds
          max_delay: 30.0     # seconds
          max_retries: 3
          jitter: true
      
      subscription_patterns:
        agent_specific:
          description: Events targeted to specific agents
          pattern: "agent.{agent_id}.{event_type}"
          example: "agent.lead_agent.feature_complete"
        
        broadcast:
          description: System-wide events
          pattern: "system.{event_type}"
          example: "system.shutdown"
        
        topic_based:
          description: Feature or domain specific events
          pattern: "{domain}.{event_type}"
          example: "feature.validation_complete"
      
  event_types:
    system:
      state_changes:
        - system_initialized
        - system_shutdown
        - error_occurred
      monitoring:
        - agent_heartbeat
        - performance_metric
        - resource_usage
    
    project_initialization:
      - project_summary_ready
      - features_identified
      - research_requested
      payload_requirements:
        project_summary_ready:
          - project_details: Dict
          - metadata: Dict
          - timestamp: datetime
    
    feature_development:
      - feature_assigned
      - research_complete
      - feature_draft_ready
      - validation_requested
      - validation_complete
      payload_requirements:
        feature_assigned:
          - feature_id: str
          - feature_details: Dict
          - assigned_to: str
        validation_complete:
          - feature_id: str
          - validation_result: Dict
          - feedback: List[str]
    
    documentation:
      - documentation_requested
      - template_selected
      - content_generated
      - documentation_complete
      payload_requirements:
        documentation_complete:
          - doc_type: str
          - content: str
          - metadata: Dict
    
  event_persistence:
    strategy: memory_agent
    retention:
      default: 24h
      system_events: 7d
      error_events: 30d
    storage:
      format: vector_store
      indexing: by_correlation_id
    
  subscription_matrix:
    lead_agent:
      publishes:
        - feature_assigned
        - documentation_requested
      subscribes:
        - project_summary_ready
        - feature_complete
        - validation_complete
    
    project_consultant:
      publishes:
        - project_summary_ready
      subscribes:
        - system_initialized
    
    feature_agent:
      publishes:
        - research_requested
        - feature_draft_ready
        - feature_complete
      subscribes:
        - feature_assigned
        - research_complete
        - validation_complete
    
    validation_agent:
      publishes:
        - validation_complete
      subscribes:
        - feature_draft_ready
    
    research_agent:
      publishes:
        - research_complete
      subscribes:
        - research_requested
    
    memory_agent:
      publishes:
        - context_updated
      subscribes:
        - "*"  # Subscribes to all events for persistence
    
  error_handling:
    event_errors:
      types:
        - subscription_error
        - publication_error
        - handler_error
        - serialization_error
      handling:
        subscription_error:
          retry: true
          log_level: ERROR
          notify: system_monitor
        publication_error:
          retry: true
          store: memory_agent
          reprocess: true
    
    recovery:
      missed_events:
        strategy: replay_from_memory
        conditions:
          - agent_restart
          - reconnection
      partial_failures:
        strategy: continue_with_logging
        notification: system_monitor 