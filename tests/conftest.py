"""
Pytest configuration and shared fixtures
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_credential():
    """Fixture to provide a mock Azure credential"""
    credential = MagicMock()
    return credential


@pytest.fixture
def mock_console():
    """Fixture to provide a mock console for testing UI output"""
    with patch('utils.common.console') as mock_console:
        yield mock_console


@pytest.fixture
def mock_logger():
    """Fixture to provide a mock logger for testing logging"""
    with patch('logging.getLogger') as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        yield mock_logger
