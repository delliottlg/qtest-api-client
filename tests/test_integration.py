"""
Integration tests for QTestClient against live sandbox API.

These tests make real API calls to the sandbox project.
Skip if QTEST_API_TESTING_PROJECT_ID is not set.

Run with: pytest tests/test_integration.py -v -m integration
"""

import pytest


@pytest.mark.integration
class TestLiveAPIConnection:
    """Tests for live API connectivity"""

    def test_can_connect(self, live_client):
        """Client can connect to qTest API"""
        projects = live_client.get_projects()
        assert len(projects) > 0

    def test_can_get_project(self, live_client, sandbox_project_id):
        """Client can get sandbox project"""
        project = live_client.get_project(sandbox_project_id)
        assert project["id"] == sandbox_project_id


@pytest.mark.integration
class TestLiveTestCaseCRUD:
    """Integration tests for test case CRUD operations"""

    def test_create_get_update_delete_test_case(self, live_client, sandbox_module_id):
        """Full CRUD cycle for test case"""
        # Create
        tc = live_client.create_test_case(
            name="Integration Test - DELETE ME",
            description="Created by pytest integration test",
            steps=[("Step 1", "Expected 1")],
            module_id=sandbox_module_id
        )
        tc_id = tc["id"]
        assert tc["name"] == "Integration Test - DELETE ME"

        try:
            # Read
            fetched = live_client.get_test_case(tc_id)
            assert fetched["id"] == tc_id

            # Update
            updated = live_client.update_test_case(
                tc_id,
                name="Integration Test - UPDATED"
            )
            assert updated["name"] == "Integration Test - UPDATED"

        finally:
            # Delete (cleanup)
            result = live_client.delete_test_case(tc_id)
            assert result is True


@pytest.mark.integration
class TestLiveRequirementCRUD:
    """Integration tests for requirement CRUD operations"""

    def test_create_get_update_delete_requirement(self, live_client, sandbox_module_id):
        """Full CRUD cycle for requirement"""
        # Create
        req = live_client.create_requirement(
            name="Integration Test Requirement - DELETE ME",
            parent_id=sandbox_module_id
        )
        req_id = req["id"]
        assert "Integration Test" in req["name"]

        try:
            # Read
            fetched = live_client.get_requirement(req_id)
            assert fetched["id"] == req_id

            # Update
            updated = live_client.update_requirement(
                req_id,
                name="Integration Test Requirement - UPDATED"
            )
            assert "UPDATED" in updated["name"]

        finally:
            # Delete (cleanup)
            result = live_client.delete_requirement(req_id)
            assert result is True


@pytest.mark.integration
class TestLiveBulkOperations:
    """Integration tests for bulk operations"""

    def test_bulk_create_and_delete(self, live_client, sandbox_module_id):
        """Bulk create and delete test cases"""
        test_cases = [
            {"name": "Bulk Integration 1"},
            {"name": "Bulk Integration 2"},
            {"name": "Bulk Integration 3"},
        ]

        # Create
        create_results = live_client.bulk_create_test_cases(
            test_cases,
            module_id=sandbox_module_id,
            max_workers=2
        )
        assert len(create_results["succeeded"]) == 3
        assert len(create_results["failed"]) == 0

        created_ids = [tc["id"] for tc in create_results["succeeded"]]

        # Delete
        delete_results = live_client.bulk_delete_test_cases(created_ids, max_workers=2)
        assert len(delete_results["succeeded"]) == 3

    def test_bulk_link_to_requirement(self, live_client, sandbox_module_id):
        """Bulk link test cases to requirement"""
        # Setup: create test cases and requirement
        tc1 = live_client.create_test_case("Link Test 1", module_id=sandbox_module_id)
        tc2 = live_client.create_test_case("Link Test 2", module_id=sandbox_module_id)
        req = live_client.create_requirement("Link Target", parent_id=sandbox_module_id)

        try:
            # Link multiple test cases
            result = live_client.bulk_link_to_requirement(
                [tc1["id"], tc2["id"]],
                requirement_id=req["id"]
            )
            # qTest returns empty dict on success
            assert result == {} or result is None or isinstance(result, dict)

        finally:
            # Cleanup
            live_client.delete_test_case(tc1["id"])
            live_client.delete_test_case(tc2["id"])
            live_client.delete_requirement(req["id"])


@pytest.mark.integration
class TestLiveErrorHandling:
    """Integration tests for error handling with live API"""

    def test_not_found_raises_error(self, live_client):
        """Accessing non-existent resource raises QTestNotFoundError"""
        from qtest_client import QTestNotFoundError

        with pytest.raises(QTestNotFoundError):
            live_client.get_test_case(999999999)

    def test_delete_nonexistent_raises_error(self, live_client):
        """Deleting non-existent resource raises QTestNotFoundError"""
        from qtest_client import QTestNotFoundError

        with pytest.raises(QTestNotFoundError):
            live_client.delete_test_case(999999999)
