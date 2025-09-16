# 0x03. Unittests and Integration Tests

## Learning Objectives

At the end of this project, you are expected to be able to explain to anyone, without the help of Google:

- The difference between unit and integration tests
- Common testing patterns such as mocking, parametrizations, and fixtures
- How to implement comprehensive test suites for Python applications

## Project Structure

```
0x03-Unittests_and_integration_tests/
├── utils.py              # Utility functions to be tested
├── client.py             # GitHub API client to be tested  
├── fixtures.py           # Test data and fixtures
├── test_utils.py         # Unit tests for utils module
├── test_client.py        # Unit and integration tests for client module
└── README.md             # This file
```

## Files Overview

### utils.py
Contains utility functions:
- `access_nested_map()`: Access nested dictionaries with key paths
- `get_json()`: Fetch JSON data from remote URLs
- `memoize()`: Decorator for method result caching

### client.py
GitHub API client implementation:
- `GithubOrgClient`: Class for interacting with GitHub organizations
- Methods for fetching org data, repositories, and license checking

### fixtures.py
Contains test data (`TEST_PAYLOAD`) with:
- Mock GitHub API responses
- Expected results for testing
- Repository data with various license types

## Testing Patterns Implemented

### 1. Unit Testing
- Testing individual functions in isolation
- Mocking external dependencies
- Testing both success and error cases

### 2. Parameterized Testing
- Using `@parameterized.expand` decorator
- Testing multiple input combinations
- Reducing code duplication in tests

### 3. Mocking
- Patching functions with `@patch` decorator
- Mocking properties with `PropertyMock`
- Simulating external API responses

### 4. Integration Testing
- Testing component interactions
- Using realistic fixtures
- Verifying end-to-end functionality

## Key Test Cases

### test_utils.py
- `TestAccessNestedMap`: Tests nested dictionary access with valid and invalid paths
- `TestGetJson`: Tests HTTP JSON fetching with mocked requests
- `TestMemoize`: Tests method result caching functionality

### test_client.py
- `TestGithubOrgClient`: Unit tests for individual methods
- `TestIntegrationGithubOrgClient`: Integration tests with real API call patterns

## Running Tests

```bash
# Install required packages
pip install parameterized

# Run all tests
python -m unittest discover

# Run specific test file
python -m unittest test_utils.py
python -m unittest test_client.py

# Run with verbose output
python -m unittest -v test_utils.py
```

## Testing Concepts Demonstrated

### Unit vs Integration Tests
- **Unit Tests**: Test individual components in isolation (e.g., `test_access_nested_map`)
- **Integration Tests**: Test component interactions (e.g., `test_public_repos_integration`)

### Mocking Patterns
- **Function Mocking**: Patching `get_json` and `requests.get`
- **Property Mocking**: Mocking properties like `_public_repos_url`
- **Side Effects**: Simulating different API responses based on input

### Parameterization
- Testing multiple input combinations efficiently
- Reducing test code duplication
- Comprehensive coverage with minimal code

## Best Practices Followed

1. **Isolation**: Each test is independent and doesn't affect others
2. **Mocking External Dependencies**: No actual HTTP calls during testing
3. **Comprehensive Coverage**: Testing both success and error cases
4. **Readable Tests**: Clear test names and structure
5. **Fixtures**: Using realistic test data from fixtures.py

## Skills Developed

- Writing effective unit and integration tests
- Using unittest framework with parameterized tests
- Mocking external dependencies and properties
- Testing error handling and edge cases
- Creating comprehensive test suites
- Understanding test-driven development principles

This project provides hands-on experience with professional Python testing practices, preparing you to write robust, maintainable test suites for real-world applications.