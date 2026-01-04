"""
qTest API Client
Direct integration with qTest Manager API - no Excel needed!
"""

import os
import requests
from typing import List, Tuple, Optional, Dict, Any
from dotenv import load_dotenv


class QTestClient:
    """Client for qTest Manager REST API"""

    def __init__(self, base_url: str = None, bearer_token: str = None, project_id: int = None):
        """
        Initialize the qTest client.

        Args:
            base_url: qTest instance URL (e.g., https://yoursite.qtestnet.com)
            bearer_token: Bearer token for authentication
            project_id: Default project ID to use

        If not provided, values are loaded from .env file.
        """
        load_dotenv()

        self.base_url = base_url or os.getenv('QTEST_BASE_URL')
        self.bearer_token = bearer_token or os.getenv('QTEST_BEARER_TOKEN')
        self.project_id = project_id or int(os.getenv('QTEST_DEFAULT_PROJECT_ID', 0))

        if not self.base_url or not self.bearer_token:
            raise ValueError("Missing QTEST_BASE_URL or QTEST_BEARER_TOKEN. Check your .env file.")

        self.api_url = f"{self.base_url}/api/v3"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': self.bearer_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _get(self, endpoint: str, params: dict = None) -> Any:
        """Make a GET request to the API"""
        url = f"{self.api_url}/{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, data: dict) -> Any:
        """Make a POST request to the API"""
        url = f"{self.api_url}/{endpoint}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        # Some endpoints return empty response (204 No Content)
        if response.status_code == 204 or not response.text:
            return {}
        return response.json()

    # ========== Projects ==========

    def get_projects(self) -> List[Dict]:
        """Get all projects accessible to this user"""
        return self._get("projects")

    def get_project(self, project_id: int = None) -> Dict:
        """Get a specific project by ID"""
        pid = project_id or self.project_id
        return self._get(f"projects/{pid}")

    # ========== Modules (Folders) ==========

    def get_modules(self, project_id: int = None, parent_id: int = None) -> List[Dict]:
        """
        Get modules (folders) for organizing test cases.

        Args:
            project_id: Project ID (uses default if not specified)
            parent_id: Parent module ID to get children of (None for root)

        Returns:
            List of module dictionaries with id, name, parent_id, etc.
        """
        pid = project_id or self.project_id
        params = {}
        if parent_id:
            params['parentId'] = parent_id
        return self._get(f"projects/{pid}/modules", params)

    def get_module_tree(self, project_id: int = None) -> List[Dict]:
        """Get full module tree structure"""
        pid = project_id or self.project_id
        return self._get(f"projects/{pid}/modules", {'expand': 'descendants'})

    # ========== Test Cases ==========

    def get_test_cases(self, project_id: int = None, module_id: int = None,
                       page: int = 1, size: int = 100, expand_steps: bool = True) -> List[Dict]:
        """
        Get test cases from a project.

        Args:
            project_id: Project ID
            module_id: Filter by module (folder)
            page: Page number (1-indexed)
            size: Results per page
            expand_steps: Include test steps in response

        Returns:
            List of test case dictionaries
        """
        pid = project_id or self.project_id
        params = {
            'page': page,
            'size': size,
            'expandSteps': str(expand_steps).lower()
        }
        if module_id:
            params['parentId'] = module_id
        return self._get(f"projects/{pid}/test-cases", params)

    def get_test_case(self, test_case_id: int, project_id: int = None,
                      expand_steps: bool = True) -> Dict:
        """Get a specific test case by ID"""
        pid = project_id or self.project_id
        params = {'expandSteps': str(expand_steps).lower()}
        return self._get(f"projects/{pid}/test-cases/{test_case_id}", params)

    def create_test_case(self, name: str,
                         description: str = '',
                         precondition: str = '',
                         steps: Optional[List[Tuple[str, str]]] = None,
                         module_id: int = None,
                         project_id: int = None) -> Dict:
        """
        Create a new test case in qTest.

        Args:
            name: Test case name
            description: Test case description (HTML supported)
            precondition: Prerequisites for the test (HTML supported)
            steps: List of tuples (step_description, expected_result)
            module_id: Parent module/folder ID (required)
            project_id: Project ID (uses default if not specified)

        Returns:
            Created test case data from API
        """
        pid = project_id or self.project_id

        if not module_id:
            raise ValueError("module_id is required to create a test case")

        # Build test steps
        test_steps = []
        if steps:
            for order, (step_desc, expected) in enumerate(steps, 1):
                test_steps.append({
                    'description': step_desc,
                    'expected': expected,
                    'order': order
                })

        data = {
            'name': name,
            'description': description,
            'precondition': precondition,
            'test_steps': test_steps
        }

        params = {'parentId': module_id}
        url = f"{self.api_url}/projects/{pid}/test-cases"
        response = self.session.post(url, json=data, params=params)
        response.raise_for_status()
        return response.json()

    # ========== Requirements (Epics) ==========

    def get_requirements(self, project_id: int = None, parent_id: int = None,
                         page: int = 1, size: int = 100) -> List[Dict]:
        """
        Get requirements (imported Jira epics) from a project.

        Args:
            project_id: Project ID (uses default if not specified)
            parent_id: Filter by parent module (optional)
            page: Page number (1-indexed)
            size: Results per page

        Returns:
            List of requirement dictionaries
        """
        pid = project_id or self.project_id
        params = {
            'page': page,
            'size': size
        }
        if parent_id:
            params['parentId'] = parent_id
        return self._get(f"projects/{pid}/requirements", params)

    def find_requirement_by_name(self, name: str, project_id: int = None) -> Optional[Dict]:
        """
        Find a requirement by name or key (e.g., 'SGD-1234').

        Args:
            name: Requirement name or Jira key to search for (case-insensitive partial match)
            project_id: Project ID (uses default if not specified)

        Returns:
            First matching requirement dict, or None if not found
        """
        requirements = self.get_requirements(project_id)
        name_lower = name.lower()
        for req in requirements:
            if name_lower in req.get('name', '').lower():
                return req
            # Also check PID field (format id like "SGD-1234")
            if 'pid' in req and name_lower in req['pid'].lower():
                return req
        return None

    def link_test_to_requirement(self, test_case_id: int, requirement_id: int,
                                  project_id: int = None) -> Dict:
        """
        Link a test case to a requirement (epic).

        Args:
            test_case_id: ID of the test case to link
            requirement_id: ID of the requirement to link to
            project_id: Project ID (uses default if not specified)

        Returns:
            Response from API
        """
        pid = project_id or self.project_id
        # Use the req-tc-links endpoint per qTest API v3 docs
        data = {
            'requirement_id': requirement_id,
            'testcase_ids': [test_case_id]
        }
        return self._post(f"projects/{pid}/req-tc-links", data)

    # ========== Releases & Test Cycles ==========

    def get_releases(self, project_id: int = None) -> List[Dict]:
        """
        Get all releases for a project.

        Args:
            project_id: Project ID (uses default if not specified)

        Returns:
            List of release dictionaries
        """
        pid = project_id or self.project_id
        return self._get(f"projects/{pid}/releases")

    def get_test_cycles(self, release_id: int = None, project_id: int = None) -> List[Dict]:
        """
        Get test cycles, optionally filtered by release.

        Args:
            release_id: Filter by release ID (optional)
            project_id: Project ID (uses default if not specified)

        Returns:
            List of test cycle dictionaries
        """
        pid = project_id or self.project_id
        params = {}
        if release_id:
            params['parentId'] = release_id
        return self._get(f"projects/{pid}/test-cycles", params)

    def add_test_to_cycle(self, test_case_id: int, cycle_id: int,
                          project_id: int = None) -> Dict:
        """
        Add a test case to a test cycle by creating a test run.

        Args:
            test_case_id: ID of the test case
            cycle_id: ID of the test cycle
            project_id: Project ID (uses default if not specified)

        Returns:
            Created test run data
        """
        pid = project_id or self.project_id
        # Create a test run under a test cycle
        params = {
            'parentId': cycle_id,
            'parentType': 'test-cycle'
        }
        data = {
            'test_case_id': test_case_id
        }
        url = f"{self.api_url}/projects/{pid}/test-runs"
        response = self.session.post(url, json=data, params=params)
        response.raise_for_status()
        return response.json()

    # ========== Test Run Execution ==========

    def create_test_run(self, test_case_id: int, parent_id: int = None,
                        parent_type: str = 'root', name: str = None,
                        project_id: int = None) -> Dict:
        """
        Create a test run from a test case.

        Args:
            test_case_id: ID of the test case to create a run from
            parent_id: ID of the parent container (0 or None for root)
            parent_type: Type of parent - 'root', 'release', 'test-cycle', or 'test-suite'
            name: Optional name for the test run
            project_id: Project ID (uses default if not specified)

        Returns:
            Created test run data
        """
        pid = project_id or self.project_id
        params = {
            'parentType': parent_type
        }
        if parent_id is not None:
            params['parentId'] = parent_id

        data = {'test_case_id': test_case_id}
        if name:
            data['name'] = name

        url = f"{self.api_url}/projects/{pid}/test-runs"
        response = self.session.post(url, json=data, params=params)
        response.raise_for_status()
        return response.json()

    def update_test_run_status(self, run_id: int, status: str,
                                note: str = None, project_id: int = None) -> Dict:
        """
        Update a test run's execution status by submitting a test log.

        Args:
            run_id: ID of the test run
            status: Status name (e.g., 'Passed', 'Failed', 'Blocked', 'Incomplete')
            note: Optional note/comment about the execution
            project_id: Project ID (uses default if not specified)

        Returns:
            Created test log data
        """
        pid = project_id or self.project_id
        data = {
            'status': status,
            'test_run_id': run_id
        }
        if note:
            data['note'] = note

        return self._post(f"projects/{pid}/test-runs/{run_id}/test-logs", data)

    # ========== Convenience Methods ==========

    def find_module_by_name(self, name: str, project_id: int = None) -> Optional[Dict]:
        """Find a module by name (case-insensitive partial match)"""
        modules = self.get_modules(project_id)
        name_lower = name.lower()
        for module in modules:
            if name_lower in module['name'].lower():
                return module
        return None

    def print_modules(self, project_id: int = None):
        """Print all modules in a readable format"""
        modules = self.get_modules(project_id)
        print(f"\n{'ID':<12} {'Name':<40} {'Parent ID'}")
        print("-" * 70)
        for m in modules:
            print(f"{m['id']:<12} {m['name']:<40} {m.get('parent_id', 'root')}")

    def print_test_cases(self, project_id: int = None, module_id: int = None, limit: int = 10):
        """Print test cases in a readable format"""
        cases = self.get_test_cases(project_id, module_id, size=limit, expand_steps=False)
        print(f"\n{'ID':<12} {'Name':<50} {'Steps'}")
        print("-" * 75)
        for tc in cases:
            step_count = len(tc.get('test_steps', []))
            name = tc['name'][:47] + '...' if len(tc['name']) > 50 else tc['name']
            print(f"{tc['id']:<12} {name:<50} {step_count}")


# Quick test when run directly
if __name__ == "__main__":
    client = QTestClient()

    print("=== Projects ===")
    projects = client.get_projects()
    for p in projects[:5]:
        print(f"  {p['id']}: {p['name']}")

    print("\n=== Modules (SGD 3.0) ===")
    client.print_modules()

    print("\n=== Sample Test Cases ===")
    client.print_test_cases(limit=5)
