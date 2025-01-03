### 1. Integration Tests
- Located in `backend/tests/integration/`
- Must be marked with `@pytest.mark.integration`
- Skip if required API keys are missing
- Create and cleanup test databases for each test
- Verify database schema before tests

### 2. Configuration

#### Test Directory Structure
```
backend/tests/
  ├── agents/         # Unit tests with mocks
  ├── integration/    # Integration tests with real components
  ├── base_test.py   # Shared test utilities
  └── conftest.py    # Fixtures and configuration
```

### 6. Database Operations
- Use real SQLite database
- Initialize test database with correct schema
- Clean up test data after each test
- Verify schema matches production
- Use transactions for test isolation 