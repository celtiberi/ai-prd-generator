# Testing Guidelines

This document contains structured guidelines for writing tests in the AI PRD Generator project. The guidelines are provided in JSON format for AI parsing while maintaining human readability.

```json
{
    "testing_guidelines": {
        "overview": {
            "description": "Guidelines for writing tests in the AI PRD Generator project",
            "scope": ["Integration tests", "Unit tests", "Test organization", "Best practices"]
        },
        "directory_structure": {
            "root": "backend/tests/",
            "components": {
                "agents/": {
                    "purpose": "Unit tests with mocks",
                    "key_files": {
                        "conftest.py": "Unit test fixtures and mocks"
                    }
                },
                "integration/": {
                    "purpose": "Integration tests with real components",
                    "requirements": ["No mocks", "Real services", "Complete workflows"]
                },
                "base_test.py": "Shared test utilities",
                "conftest.py": "Integration test fixtures (real components)"
            }
        },
        "integration_tests": {
            "location": "backend/tests/integration/",
            "requirements": [
                "Never use mocks - all components must be real",
                "Must use @pytest.mark.integration decorator",
                "Must use real external services (OpenAI, Tavily)",
                "Must handle API keys and credentials properly"
            ],
            "example": {
                "description": "Complete workflow test",
                "code": [
                    "@pytest.mark.integration",
                    "@pytest.mark.skipif(not settings.OPENAI_API_KEY, reason=\"OPENAI_API_KEY not set\")",
                    "@pytest.mark.asyncio",
                    "async def test_complete_workflow(self, agent_system, sample_project_data, caplog):",
                    "    caplog.set_level(logging.DEBUG)",
                    "    self.subscribe_to_events([\"event_type\"])",
                    "    try:",
                    "        lead_agent = agent_system[\"lead\"]",
                    "        await lead_agent.some_method(sample_project_data)",
                    "        await asyncio.sleep(0.2)",
                    "        assert self.assert_event_received(\"event_type\")[0]",
                    "    finally:",
                    "        self.cleanup_subscriptions()"
                ]
            }
        },
        "unit_tests": {
            "location": "backend/tests/agents/",
            "requirements": [
                "Use mocks for external services",
                "Keep mocks in agents/conftest.py",
                "Fast execution",
                "No external dependencies"
            ],
            "example": {
                "description": "Feature delegation test",
                "code": [
                    "@pytest.mark.asyncio",
                    "async def test_feature_delegation(self, mock_llm_service, caplog):",
                    "    caplog.set_level(logging.DEBUG)",
                    "    self.subscribe_to_events([\"feature_request\"])",
                    "    try:",
                    "        agent = LeadAgent(llm_service=mock_llm_service)",
                    "        await agent.process_feature(sample_feature)",
                    "        assert self.assert_event_received(\"feature_request\")[0]",
                    "    finally:",
                    "        self.cleanup_subscriptions()"
                ]
            }
        },
        "test_base_class": {
            "name": "BaseAgentTest",
            "features": {
                "event_subscription": "subscribe_to_events(topics: List[str])",
                "event_verification": "assert_event_received(event_type: str)",
                "cleanup": "cleanup_subscriptions()"
            }
        },
        "database_testing": {
            "requirements": [
                "Use real SQLite database",
                "Initialize with correct schema",
                "Clean up test data",
                "Use transactions for isolation",
                "Handle errors gracefully"
            ],
            "example": {
                "verification": [
                    "cursor = memory_agent.sql_db.cursor()",
                    "cursor.execute(\"SELECT * FROM features WHERE name = ?\", (name,))",
                    "result = cursor.fetchone()",
                    "assert result is not None"
                ]
            }
        },
        "event_handling": {
            "patterns": {
                "subscription": [
                    "self.subscribe_to_events([\"event_type\"])",
                    "try:",
                    "    # Test code",
                    "finally:",
                    "    self.cleanup_subscriptions()"
                ],
                "verification": [
                    "assert self.assert_event_received(\"event_type\")[0]"
                ]
            },
            "timing": {
                "delays": "Use asyncio.sleep(0.2) after operations that publish events",
                "cleanup": "Always use try/finally for subscription cleanup"
            }
        },
        "external_services": {
            "rate_limits": {
                "description": "Handling API rate limits and quotas",
                "openai_models": {
                    "testing": "gpt-3.5-turbo",
                    "production": "gpt-4-turbo-preview",
                    "rationale": [
                        "Use cheaper models for testing to avoid quota issues",
                        "gpt-3.5-turbo is sufficient for testing API integration",
                        "Save gpt-4 quota for production use"
                    ]
                },
                "strategies": [
                    "Use exponential backoff for retries",
                    "Cache API responses in test environment",
                    "Mock responses after first real call",
                    "Skip tests when quota exceeded",
                    "Use separate test API keys"
                ],
                "implementation": {
                    "retry_pattern": [
                        "initial_delay = 1",
                        "max_retries = 3",
                        "backoff_factor = 2"
                    ],
                    "skip_conditions": [
                        "@pytest.mark.skipif(",
                        "    is_quota_exceeded(),",
                        "    reason=\"API quota exceeded\"",
                        ")"
                    ],
                    "caching": {
                        "location": "tests/fixtures/api_responses/",
                        "strategy": "Store first successful response, use for subsequent tests"
                    }
                }
            },
            "error_handling": {
                "429_too_many_requests": {
                    "actions": [
                        "Log warning with quota status",
                        "Skip remaining API-dependent tests",
                        "Fall back to cached responses",
                        "Mark tests as skipped rather than failed"
                    ]
                }
            }
        }
    }
}
```

## Quick Reference

Key points from the guidelines:

1. **Directory Structure**
   - `backend/tests/agents/` - Unit tests
   - `backend/tests/integration/` - Integration tests
   - `backend/tests/base_test.py` - Shared utilities
   - `backend/tests/conftest.py` - Common fixtures

2. **Test Types**
   - Integration Tests: Real components, no mocks
   - Unit Tests: Use mocks, fast execution

3. **OpenAI Models**
   - Testing: `gpt-3.5-turbo`
   - Production: `gpt-4-turbo-preview`

4. **Error Handling**
   - Handle rate limits
   - Cache responses when possible
   - Skip tests on quota exceeded

For full details, parse the JSON content above. 