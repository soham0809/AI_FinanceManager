# Test Suite README

## Overview

Comprehensive Pytest-based test suite for the AI Financial Co-Pilot backend API, covering all 50+ endpoints across 9 route modules.

## Quick Start

### Install Dependencies
```bash
cd backend
python -m pip install -r requirements.txt
python -m pip install pytest pytest-asyncio pytest-cov httpx faker
```

### Run All Tests
```bash
# Run all tests (excluding slow tests)
python -m pytest tests/ -v -m "not slow"

# Run with coverage report
python -m pytest tests/ -v --cov=app --cov-report=html

# Run specific test module
python -m pytest tests/test_auth_routes.py -v

# Run tests with specific marker
python -m pytest tests/ -v -m auth
```

## Test Organization

```
tests/
├── conftest.py                   # Shared fixtures and configuration
├── test_auth_routes.py          # Authentication (12 tests)
├── test_transaction_routes.py   # Transactions (17 tests)
├── test_analytics_routes.py     # Analytics (11 tests)
├── test_monthly_routes.py       # Monthly analytics (7 tests)
├── test_chatbot_routes.py       # Chatbot (5 tests - marked slow)
├── test_enhanced_chatbot_routes.py  # Enhanced chatbot (10 tests - marked slow)
├── test_quick_routes.py         # Async/batch routes (9 tests - marked slow)
├── test_predictions_routes.py   # Predictions/ML (6 tests)
├── test_categorize_routes.py    # Categorization (3 tests)
└── test_health_routes.py        # Health checks (3 tests)
```

## Test Markers

Tests are marked for selective execution:

- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.transactions` - Transaction tests
- `@pytest.mark.analytics` - Analytics tests
- `@pytest.mark.chatbot` - Chatbot tests
- `@pytest.mark.slow` - Tests that take longer (>5s)
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests

Run specific markers:
```bash
pytest tests/ -v -m auth
pytest tests/ -v -m "not slow"
```

## Fixtures

### Database Fixtures
- `test_db` - Fresh in-memory SQLite database for each test
- `client` - FastAPI TestClient with database override

### Authentication Fixtures
- `test_user` - Pre-created test user
- `auth_headers` - Authorization headers with valid JWT token
- `another_user` - Second test user for multi-user tests

### Test Data Fixtures
- `sample_transactions` - Set of diverse test transactions
- `sample_sms_messages` - Sample SMS messages for parsing tests

## Test Coverage

Current coverage: **~85%**

View detailed coverage report:
```bash
python -m pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html
```

## Writing New Tests

### Basic Test Structure
```python
import pytest
from fastapi.testclient import TestClient

class TestMyRoutes:
    \"\"\"Test my new routes\"\"\"
    
    def test_my_endpoint(self, client: TestClient, auth_headers):
        \"\"\"Test description\"\"\"
        response = client.get("/my-endpoint", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "expected_field" in data
```

### Using Fixtures
```python
def test_with_user_data(self, client, auth_headers, sample_transactions):
    \"\"\"Use existing fixtures for setup\"\"\"
    # Database already has sample_transactions from fixture
    response = client.get("/transactions", headers=auth_headers)
    assert len(response.json()) == len(sample_transactions)
```

### Testing Authentication
```python
def test_requires_auth(self, client):
    \"\"\"Test endpoint requires authentication\"\"\"
    response = client.get("/protected-endpoint")
    assert response.status_code == 401

def test_with_auth(self, client, auth_headers):
    \"\"\"Test with valid authentication\"\"\"
    response = client.get("/protected-endpoint", headers=auth_headers)
    assert response.status_code == 200
```

## Test Results

Latest run: **56/57 tests passed (98.2%)**

See `test_results_metrics.md` for detailed metrics and research paper data.

## Performance

- **Total Execution Time**: ~4.34 seconds (excluding slow tests)
- **Average Test Time**: 76ms
- **Fastest Tests**: Health checks (<10ms)

## Continuous Integration

Add to CI/CD pipeline:
```yaml
# .github/workflows/tests.yml
- name: Run Tests
  run: |
    pip install -r requirements.txt
    pip install pytest pytest-cov
    pytest tests/ -v --cov=app --cov-report=xml
```

## Troubleshooting

### ModuleNotFoundError
```bash
# Install missing dependencies
pip install -r requirements.txt
```

### Database Errors
- Tests use in-memory SQLite
- Each test gets fresh database (function-scoped)
- No manual cleanup needed

### Authentication Failures
- Check `conftest.py` for auth fixtures
- Verify `AuthController` is working
- Ensure JWT token creation is functional

## Best Practices

1. **Isolation**: Each test should be independent
2. **Fixtures**: Use fixtures for common setup
3. **Assertions**: Clear, specific assertions
4. **Naming**: Descriptive test names (test_what_when_expected)
5. **Markers**: Mark slow or integration tests appropriately

## Future Enhancements

- [ ] Add performance benchmarking tests
- [ ] Increase coverage to 90%+
- [ ] Add load testing suite
- [ ] Add API contract tests (OpenAPI validation)
- [ ] Add security testing (OWASP Top 10)

## Contact

For questions about tests, see the implementation plan or contact the development team.
