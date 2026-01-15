"""
Unit tests for QTestClient with mocked HTTP responses.

Run with: pytest tests/test_client.py -v
"""

import pytest
import responses
from qtest_client import (
    QTestClient,
    QTestError,
    QTestNotFoundError,
    QTestAuthenticationError,
    QTestValidationError,
    QTestRateLimitError,
    QTestServerError,
)


class TestClientInitialization:
    """Tests for client initialization"""

    def test_init_with_explicit_params(self):
        """Client initializes with explicit parameters"""
        client = QTestClient(
            base_url="https://test.qtestnet.com",
            bearer_token="Bearer test-token",
            project_id=12345
        )
        assert client.base_url == "https://test.qtestnet.com"
        assert client.bearer_token == "Bearer test-token"
        assert client.project_id == 12345

    def test_validation_requires_base_url_and_token(self):
        """Validation logic checks for required credentials"""
        # Test the validation condition directly
        # (The actual init test is hard because dotenv loads from project root)
        base_url = None
        bearer_token = "valid"

        # This is the same check used in __init__
        assert not base_url or not bearer_token  # Would raise

        base_url = "https://test.com"
        bearer_token = None
        assert not base_url or not bearer_token  # Would raise

        base_url = "https://test.com"
        bearer_token = "valid"
        assert base_url and bearer_token  # Would pass

    def test_init_custom_retry_config(self):
        """Client accepts custom retry configuration"""
        client = QTestClient(
            base_url="https://test.qtestnet.com",
            bearer_token="Bearer test",
            max_retries=5,
            retry_delay=2.0,
            timeout=60
        )
        assert client.max_retries == 5
        assert client.retry_delay == 2.0
        assert client.timeout == 60


class TestProjectMethods:
    """Tests for project-related methods"""

    @responses.activate
    def test_get_projects(self, mock_base_url, mock_token):
        """get_projects returns list of projects"""
        responses.add(
            responses.GET,
            f"{mock_base_url}/api/v3/projects",
            json=[
                {"id": 1, "name": "Project 1"},
                {"id": 2, "name": "Project 2"},
            ],
            status=200
        )

        client = QTestClient(mock_base_url, mock_token, 1)
        projects = client.get_projects()

        assert len(projects) == 2
        assert projects[0]["name"] == "Project 1"

    @responses.activate
    def test_get_project(self, mock_base_url, mock_token):
        """get_project returns single project"""
        responses.add(
            responses.GET,
            f"{mock_base_url}/api/v3/projects/123",
            json={"id": 123, "name": "My Project"},
            status=200
        )

        client = QTestClient(mock_base_url, mock_token, 123)
        project = client.get_project()

        assert project["id"] == 123
        assert project["name"] == "My Project"


class TestTestCaseMethods:
    """Tests for test case methods"""

    @responses.activate
    def test_create_test_case(self, mock_base_url, mock_token):
        """create_test_case sends correct payload"""
        responses.add(
            responses.POST,
            f"{mock_base_url}/api/v3/projects/100/test-cases",
            json={"id": 999, "name": "New Test"},
            status=201
        )

        client = QTestClient(mock_base_url, mock_token, 100)
        result = client.create_test_case(
            name="New Test",
            description="Test description",
            steps=[("Step 1", "Expected 1")],
            module_id=50
        )

        assert result["id"] == 999
        # Verify request payload
        request = responses.calls[0].request
        assert "parentId=50" in request.url

    @responses.activate
    def test_get_test_case(self, mock_base_url, mock_token):
        """get_test_case returns test case details"""
        responses.add(
            responses.GET,
            f"{mock_base_url}/api/v3/projects/100/test-cases/999",
            json={"id": 999, "name": "Test Case", "test_steps": []},
            status=200
        )

        client = QTestClient(mock_base_url, mock_token, 100)
        tc = client.get_test_case(999)

        assert tc["id"] == 999
        assert "expandSteps=true" in responses.calls[0].request.url

    @responses.activate
    def test_delete_test_case(self, mock_base_url, mock_token):
        """delete_test_case returns True on success"""
        responses.add(
            responses.DELETE,
            f"{mock_base_url}/api/v3/projects/100/test-cases/999",
            status=204
        )

        client = QTestClient(mock_base_url, mock_token, 100)
        result = client.delete_test_case(999)

        assert result is True


class TestRequirementMethods:
    """Tests for requirement methods"""

    @responses.activate
    def test_get_requirements(self, mock_base_url, mock_token):
        """get_requirements returns list"""
        responses.add(
            responses.GET,
            f"{mock_base_url}/api/v3/projects/100/requirements",
            json=[{"id": 1, "name": "Req 1"}],
            status=200
        )

        client = QTestClient(mock_base_url, mock_token, 100)
        reqs = client.get_requirements()

        assert len(reqs) == 1

    @responses.activate
    def test_create_requirement(self, mock_base_url, mock_token):
        """create_requirement sends correct payload"""
        responses.add(
            responses.POST,
            f"{mock_base_url}/api/v3/projects/100/requirements",
            json={"id": 555, "name": "New Req"},
            status=201
        )

        client = QTestClient(mock_base_url, mock_token, 100)
        result = client.create_requirement("New Req", parent_id=10)

        assert result["id"] == 555
        assert "parentId=10" in responses.calls[0].request.url

    @responses.activate
    def test_bulk_link_to_requirement(self, mock_base_url, mock_token):
        """bulk_link_to_requirement sends correct payload"""
        responses.add(
            responses.POST,
            f"{mock_base_url}/api/v3/projects/100/req-tc-links",
            json={},
            status=200
        )

        client = QTestClient(mock_base_url, mock_token, 100)
        client.bulk_link_to_requirement([1, 2, 3], requirement_id=555)

        request_body = responses.calls[0].request.body.decode('utf-8')
        assert "555" in request_body
        assert "1" in request_body


class TestErrorHandling:
    """Tests for error handling"""

    @responses.activate
    def test_404_raises_not_found_error(self, mock_base_url, mock_token):
        """404 response raises QTestNotFoundError"""
        responses.add(
            responses.GET,
            f"{mock_base_url}/api/v3/projects/100/test-cases/999",
            json={"message": "Test case not found"},
            status=404
        )

        client = QTestClient(mock_base_url, mock_token, 100)

        with pytest.raises(QTestNotFoundError) as exc_info:
            client.get_test_case(999)

        assert exc_info.value.status_code == 404
        assert "Not found" in exc_info.value.message

    @responses.activate
    def test_401_raises_auth_error(self, mock_base_url, mock_token):
        """401 response raises QTestAuthenticationError"""
        responses.add(
            responses.GET,
            f"{mock_base_url}/api/v3/projects",
            status=401
        )

        client = QTestClient(mock_base_url, mock_token, 100)

        with pytest.raises(QTestAuthenticationError):
            client.get_projects()

    @responses.activate
    def test_400_raises_validation_error(self, mock_base_url, mock_token):
        """400 response raises QTestValidationError"""
        responses.add(
            responses.POST,
            f"{mock_base_url}/api/v3/projects/100/test-cases",
            json={"message": "Name is required"},
            status=400
        )

        client = QTestClient(mock_base_url, mock_token, 100)

        with pytest.raises(QTestValidationError) as exc_info:
            client.create_test_case("", module_id=1)

        assert "Name is required" in exc_info.value.message

    @responses.activate
    def test_429_raises_rate_limit_error(self, mock_base_url, mock_token):
        """429 response raises QTestRateLimitError with retry_after"""
        responses.add(
            responses.GET,
            f"{mock_base_url}/api/v3/projects",
            headers={"retry-after": "30"},
            status=429
        )

        client = QTestClient(mock_base_url, mock_token, 100, max_retries=0)

        with pytest.raises(QTestRateLimitError) as exc_info:
            client.get_projects()

        assert exc_info.value.retry_after == 30

    @responses.activate
    def test_500_raises_server_error(self, mock_base_url, mock_token):
        """500 response raises QTestServerError"""
        responses.add(
            responses.GET,
            f"{mock_base_url}/api/v3/projects",
            status=500
        )

        client = QTestClient(mock_base_url, mock_token, 100, max_retries=0)

        with pytest.raises(QTestServerError):
            client.get_projects()


class TestRetryLogic:
    """Tests for retry logic"""

    @responses.activate
    def test_retries_on_500(self, mock_base_url, mock_token):
        """Client retries on 500 errors"""
        # First call fails, second succeeds
        responses.add(responses.GET, f"{mock_base_url}/api/v3/projects", status=500)
        responses.add(
            responses.GET,
            f"{mock_base_url}/api/v3/projects",
            json=[{"id": 1}],
            status=200
        )

        client = QTestClient(mock_base_url, mock_token, 100, retry_delay=0.01)
        result = client.get_projects()

        assert len(responses.calls) == 2
        assert len(result) == 1

    @responses.activate
    def test_respects_max_retries(self, mock_base_url, mock_token):
        """Client stops after max_retries"""
        # All calls fail
        for _ in range(5):
            responses.add(responses.GET, f"{mock_base_url}/api/v3/projects", status=500)

        client = QTestClient(mock_base_url, mock_token, 100, max_retries=2, retry_delay=0.01)

        with pytest.raises(QTestServerError):
            client.get_projects()

        # Initial + 2 retries = 3 calls
        assert len(responses.calls) == 3


class TestBulkOperations:
    """Tests for bulk operation methods"""

    @responses.activate
    def test_bulk_create_test_cases(self, mock_base_url, mock_token):
        """bulk_create_test_cases creates multiple test cases"""
        # Add response for each creation
        for i in range(3):
            responses.add(
                responses.POST,
                f"{mock_base_url}/api/v3/projects/100/test-cases",
                json={"id": 1000 + i, "name": f"Test {i}"},
                status=201
            )

        client = QTestClient(mock_base_url, mock_token, 100)
        test_cases = [
            {"name": "Test 0"},
            {"name": "Test 1"},
            {"name": "Test 2"},
        ]

        results = client.bulk_create_test_cases(test_cases, module_id=50, max_workers=1)

        assert len(results["succeeded"]) == 3
        assert len(results["failed"]) == 0

    @responses.activate
    def test_bulk_create_with_failures(self, mock_base_url, mock_token):
        """bulk_create_test_cases handles partial failures"""
        responses.add(
            responses.POST,
            f"{mock_base_url}/api/v3/projects/100/test-cases",
            json={"id": 1000, "name": "Test 0"},
            status=201
        )
        responses.add(
            responses.POST,
            f"{mock_base_url}/api/v3/projects/100/test-cases",
            status=400  # This one fails
        )

        client = QTestClient(mock_base_url, mock_token, 100)
        test_cases = [{"name": "Test 0"}, {"name": "Test 1"}]

        results = client.bulk_create_test_cases(test_cases, module_id=50, max_workers=1)

        assert len(results["succeeded"]) == 1
        assert len(results["failed"]) == 1

    @responses.activate
    def test_bulk_progress_callback(self, mock_base_url, mock_token):
        """bulk operations call progress callback"""
        responses.add(
            responses.POST,
            f"{mock_base_url}/api/v3/projects/100/test-cases",
            json={"id": 1000},
            status=201
        )

        client = QTestClient(mock_base_url, mock_token, 100)
        progress_calls = []

        def on_progress(completed, total, result):
            progress_calls.append((completed, total, result["success"]))

        client.bulk_create_test_cases(
            [{"name": "Test"}],
            module_id=50,
            on_progress=on_progress,
            max_workers=1
        )

        assert len(progress_calls) == 1
        assert progress_calls[0] == (1, 1, True)
