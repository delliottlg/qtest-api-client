"""
Pytest configuration and shared fixtures for qTest API Client tests.
"""

import os
import pytest
import responses
from dotenv import load_dotenv

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qtest_client import QTestClient


# Load environment variables
load_dotenv()


@pytest.fixture
def mock_base_url():
    """Base URL for mocked API tests"""
    return "https://mock.qtestnet.com"


@pytest.fixture
def mock_token():
    """Bearer token for mocked tests"""
    return "Bearer mock-token-12345"


@pytest.fixture
def mock_project_id():
    """Project ID for mocked tests"""
    return 99999


@pytest.fixture
@responses.activate
def mock_client(mock_base_url, mock_token, mock_project_id):
    """
    QTestClient configured with mock credentials.
    Use with @responses.activate decorator in tests.
    """
    return QTestClient(
        base_url=mock_base_url,
        bearer_token=mock_token,
        project_id=mock_project_id
    )


@pytest.fixture
def sandbox_project_id():
    """
    Sandbox project ID for integration tests.
    Returns None if not configured (skips integration tests).
    """
    project_id = os.getenv('QTEST_API_TESTING_PROJECT_ID')
    return int(project_id) if project_id else None


@pytest.fixture
def sandbox_module_id():
    """Module ID in sandbox for creating test data"""
    return 68180618  # 'Created via API' module


@pytest.fixture
def live_client(sandbox_project_id):
    """
    QTestClient configured for live API tests against sandbox.
    Skips test if sandbox not configured.
    """
    if not sandbox_project_id:
        pytest.skip("Sandbox project not configured (QTEST_API_TESTING_PROJECT_ID)")

    return QTestClient(project_id=sandbox_project_id)


# Markers for test categories
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "unit: Unit tests with mocked responses (fast, no API calls)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests against live sandbox API (slow)"
    )
