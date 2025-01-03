# Testing Guidelines

This document contains structured guidelines for writing tests in the AI PRD Generator project. The guidelines are provided in YAML format for AI parsing while maintaining human readability.

```yaml
testing:
  overview:
    description: Comprehensive testing strategy for multi-agent systems
    principles:
      - Test-driven development
      - Deterministic agent behavior
      - Comprehensive coverage
      - Isolated component testing
   
  test_types:
    unit_tests:
      scope: Individual agent behavior
      tools: pytest
      coverage_target: 90%
      key_areas:
        - Agent initialization
        - Event handling
        - State management
        - Error handling
     
    integration_tests:
      scope: Agent interactions
      tools: pytest-asyncio
      coverage_target: 85%
      key_areas:
        - Event flow
        - Multi-agent coordination
        - End-to-end workflows
     
    llm_tests:
      scope: AI model interactions
      strategy: Response mocking
      considerations:
        - Deterministic behavior
        - Cost management
        - Rate limiting
        - Response validation
     
  agent_testing:
    project_consultant:
      focus:
        - User interaction flow
        - Requirements extraction
        - Summary generation
      mocks_needed:
        - LLM responses
        - User inputs
     
    lead_agent:
      focus:
        - Workflow coordination
        - Feature delegation
        - Documentation generation
      mocks_needed:
        - Feature agent responses
        - Validation results
     
    feature_agent:
      focus:
        - Research integration
        - Specification development
        - Validation interaction
      mocks_needed:
        - Research results
        - Validation feedback
     
  test_fixtures:
    common:
      - Mock LLM service
      - Sample project data
      - Event bus setup
    specialized:
      - API response fixtures
      - Validation scenarios
      - Documentation templates
     
  continuous_integration:
    pipeline:
      - Static type checking
      - Unit tests
      - Integration tests
      - Coverage reporting
    requirements:
      - All tests must pass
      - Coverage thresholds met
      - No type errors

  documentation_validation:
    event_system:
      test_cases:
        - Verify all events have complete payload definitions
        - Check subscription matrix completeness
        - Validate error handling coverage
        - Test persistence strategy definition
      coverage_requirements:
        - Event type definitions: 100%
        - Subscription patterns: 100%
        - Error handling: 100%
        - Agent interactions: 100%
```

## Quick Reference

1. **Directory Structure**
   - `backend/tests/agents/` - Unit tests
   - `backend/tests/integration/` - Integration tests
   - `backend/tests/base_test.py` - Shared utilities
   - `backend/tests/conftest.py` - Common fixtures

2. **Test Types**
   - Unit Tests: Individual agent behavior
   - Integration Tests: Agent interactions
   - LLM Tests: AI model interaction testing

3. **Testing Considerations**
   - Deterministic behavior in AI interactions
   - Proper event flow validation
   - Comprehensive agent coverage
   - Cost-effective LLM testing

4. **Agent-Specific Testing**
   - Project Consultant: User interaction flows
   - Lead Agent: Coordination and delegation
   - Feature Agents: Research and validation
   - Memory Agent: Data persistence

For full details, parse the YAML content above. 