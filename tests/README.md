# FabricFriend Tests

This directory contains the test suite for FabricFriend.

## Structure

- `test_module_loader.py`: Tests for the module loader utility
- `test_common_utils.py`: Tests for common utilities
- `test_main.py`: Tests for the main application
- `test_module_integration.py`: Integration tests for module loading
- `conftest.py`: Shared pytest fixtures
- `setup.py`: Setup script for installing test dependencies

## Running Tests

To run the test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=utils --cov=main --cov-report=term-missing

# Run specific test file
pytest tests/test_module_loader.py

# Run specific test
pytest tests/test_module_loader.py::TestModuleLoader::test_load_and_run_with_default_command
```

## Adding Tests

When adding new tests:

1. Follow the naming convention: `test_*.py` for files, `Test*` for classes, and `test_*` for functions
2. Use appropriate fixtures from `conftest.py` or create new ones if needed
3. Mock external dependencies to avoid real API calls
4. Focus on testing behavior, not implementation details

## Coverage Focus

The test suite focuses on:
- Module loader functionality
- Common utilities
- Main application flow
- Module integration

It explicitly avoids testing:
- Module-specific business logic
- Authentication code

This keeps the tests focused and maintainable.
