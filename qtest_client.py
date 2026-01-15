"""
qTest API Client
Direct integration with qTest Manager API - no Excel needed!
"""

import os
import time
import requests
from typing import List, Tuple, Optional, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv


# ========== Custom Exceptions ==========

class QTestError(Exception):
    """Base exception for qTest API errors"""
    def __init__(self, message: str, status_code: int = None, response: requests.Response = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class QTestAuthenticationError(QTestError):
    """Authentication failed (401) - invalid or expired token"""
    pass


class QTestPermissionError(QTestError):
    """Permission denied (403) - user lacks required permissions"""
    pass


class QTestNotFoundError(QTestError):
    """Resource not found (404) - item doesn't exist or was deleted"""
    pass


class QTestValidationError(QTestError):
    """Validation failed (400/412) - invalid data submitted"""
    pass


class QTestRateLimitError(QTestError):
    """Rate limit exceeded (429) - too many requests"""
    def __init__(self, message: str, retry_after: int = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class QTestServerError(QTestError):
    """Server error (5xx) - qTest internal error"""
    pass


class QTestClient:
    """Client for qTest Manager REST API"""

    # Default retry configuration
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_DELAY = 1.0  # seconds
    DEFAULT_TIMEOUT = 30  # seconds

    def __init__(self, base_url: str = None, bearer_token: str = None, project_id: int = None,
                 max_retries: int = None, retry_delay: float = None, timeout: int = None):
        """
        Initialize the qTest client.

        Args:
            base_url: qTest instance URL (e.g., https://yoursite.qtestnet.com)
            bearer_token: Bearer token for authentication
            project_id: Default project ID to use
            max_retries: Max retry attempts for transient failures (default: 3)
            retry_delay: Base delay between retries in seconds (default: 1.0)
            timeout: Request timeout in seconds (default: 30)

        If not provided, values are loaded from .env file.
        """
        load_dotenv()

        self.base_url = base_url or os.getenv('QTEST_BASE_URL')
        self.bearer_token = bearer_token or os.getenv('QTEST_BEARER_TOKEN')
        self.project_id = project_id or int(os.getenv('QTEST_DEFAULT_PROJECT_ID', 0))

        if not self.base_url or not self.bearer_token:
            raise ValueError("Missing QTEST_BASE_URL or QTEST_BEARER_TOKEN. Check your .env file.")

        # Retry configuration
        self.max_retries = max_retries if max_retries is not None else self.DEFAULT_MAX_RETRIES
        self.retry_delay = retry_delay if retry_delay is not None else self.DEFAULT_RETRY_DELAY
        self.timeout = timeout if timeout is not None else self.DEFAULT_TIMEOUT

        self.api_url = f"{self.base_url}/api/v3"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': self.bearer_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _handle_error(self, response: requests.Response, context: str = None) -> None:
        """
        Convert HTTP errors to appropriate QTestError exceptions.

        Args:
            response: The requests Response object
            context: Optional context string (e.g., "test case 12345")
        """
        status = response.status_code
        ctx = f" ({context})" if context else ""

        # Try to extract error message from response body
        try:
            body = response.json()
            api_message = body.get('message', '') or body.get('error', '')
        except Exception:
            api_message = response.text[:200] if response.text else ''

        if status == 400:
            raise QTestValidationError(
                f"Invalid request{ctx}: {api_message or 'Bad request data'}",
                status_code=status, response=response
            )
        elif status == 401:
            raise QTestAuthenticationError(
                f"Authentication failed{ctx}: Check your bearer token",
                status_code=status, response=response
            )
        elif status == 403:
            raise QTestPermissionError(
                f"Permission denied{ctx}: User lacks required permissions",
                status_code=status, response=response
            )
        elif status == 404:
            raise QTestNotFoundError(
                f"Not found{ctx}: Resource doesn't exist or was deleted",
                status_code=status, response=response
            )
        elif status == 412:
            raise QTestValidationError(
                f"Precondition failed{ctx}: {api_message or 'Required fields missing'}",
                status_code=status, response=response
            )
        elif status == 429:
            retry_after = int(response.headers.get('retry-after', 60))
            raise QTestRateLimitError(
                f"Rate limit exceeded{ctx}: Retry after {retry_after}s",
                status_code=status, response=response, retry_after=retry_after
            )
        elif 500 <= status < 600:
            raise QTestServerError(
                f"qTest server error{ctx}: {api_message or f'HTTP {status}'}",
                status_code=status, response=response
            )
        else:
            raise QTestError(
                f"API error{ctx}: HTTP {status} - {api_message or response.reason}",
                status_code=status, response=response
            )

    def _request(self, method: str, endpoint: str, params: dict = None,
                 data: dict = None, context: str = None) -> Any:
        """
        Make an HTTP request with retry logic for transient failures.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            data: JSON body data
            context: Context string for error messages

        Returns:
            Parsed JSON response or empty dict for 204 responses
        """
        url = f"{self.api_url}/{endpoint}"
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    timeout=self.timeout
                )

                # Success
                if response.ok:
                    if response.status_code == 204 or not response.text:
                        return {}
                    return response.json()

                # Handle rate limiting with retry
                if response.status_code == 429 and attempt < self.max_retries:
                    retry_after = int(response.headers.get('retry-after', self.retry_delay * (2 ** attempt)))
                    time.sleep(retry_after)
                    continue

                # Handle server errors with retry
                if response.status_code >= 500 and attempt < self.max_retries:
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue

                # Non-retryable error
                self._handle_error(response, context)

            except requests.exceptions.Timeout as e:
                last_exception = e
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                raise QTestError(
                    f"Request timeout after {self.timeout}s ({context or endpoint})",
                    response=None
                )

            except requests.exceptions.ConnectionError as e:
                last_exception = e
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                raise QTestError(
                    f"Connection failed: {str(e)} ({context or endpoint})",
                    response=None
                )

        # Should not reach here, but just in case
        raise QTestError(f"Request failed after {self.max_retries} retries", response=None)

    def _get(self, endpoint: str, params: dict = None, context: str = None) -> Any:
        """Make a GET request to the API"""
        return self._request('GET', endpoint, params=params, context=context)

    def _post(self, endpoint: str, data: dict, context: str = None) -> Any:
        """Make a POST request to the API"""
        return self._request('POST', endpoint, data=data, context=context)

    def _put(self, endpoint: str, data: dict, context: str = None) -> Any:
        """Make a PUT request to the API"""
        return self._request('PUT', endpoint, data=data, context=context)

    def _delete(self, endpoint: str, context: str = None) -> Any:
        """Make a DELETE request to the API"""
        return self._request('DELETE', endpoint, context=context)

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

        return self._request(
            'POST', f"projects/{pid}/test-cases",
            params={'parentId': module_id}, data=data,
            context=f"create test case '{name}'"
        )

    def update_test_case(self, test_case_id: int, name: str = None,
                         description: str = None, precondition: str = None,
                         steps: Optional[List[Tuple[str, str]]] = None,
                         project_id: int = None) -> Dict:
        """
        Update an existing test case.

        Args:
            test_case_id: ID of test case to update
            name: New name (optional)
            description: New description (optional)
            precondition: New precondition (optional)
            steps: New steps as list of (description, expected) tuples (optional)
            project_id: Project ID (uses default if not specified)

        Returns:
            Updated test case data
        """
        pid = project_id or self.project_id

        # Build update data - only include fields that are provided
        data = {}
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        if precondition is not None:
            data['precondition'] = precondition
        if steps is not None:
            test_steps = []
            for order, (step_desc, expected) in enumerate(steps, 1):
                test_steps.append({
                    'description': step_desc,
                    'expected': expected,
                    'order': order
                })
            data['test_steps'] = test_steps

        return self._put(
            f"projects/{pid}/test-cases/{test_case_id}", data,
            context=f"test case {test_case_id}"
        )

    def delete_test_case(self, test_case_id: int, project_id: int = None) -> bool:
        """
        Delete a test case.

        Args:
            test_case_id: ID of test case to delete
            project_id: Project ID (uses default if not specified)

        Returns:
            True if deleted successfully
        """
        pid = project_id or self.project_id
        self._delete(f"projects/{pid}/test-cases/{test_case_id}", context=f"test case {test_case_id}")
        return True

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

    def get_requirement(self, requirement_id: int, project_id: int = None) -> Dict:
        """
        Get a specific requirement by ID.

        Args:
            requirement_id: ID of the requirement
            project_id: Project ID (uses default if not specified)

        Returns:
            Requirement dictionary with properties, name, etc.
        """
        pid = project_id or self.project_id
        return self._get(f"projects/{pid}/requirements/{requirement_id}")

    def create_requirement(self, name: str, parent_id: int,
                           description: str = None,
                           properties: List[Dict] = None,
                           project_id: int = None) -> Dict:
        """
        Create a new requirement.

        Args:
            name: Requirement name (required)
            parent_id: Parent module ID (required - requirements must be in a module)
            description: Requirement description (optional)
            properties: List of property dicts with field_id and field_value (optional)
            project_id: Project ID (uses default if not specified)

        Returns:
            Created requirement data with id, name, web_url, etc.
        """
        pid = project_id or self.project_id

        data = {'name': name}
        if properties:
            data['properties'] = properties

        return self._request(
            'POST', f"projects/{pid}/requirements",
            params={'parentId': parent_id}, data=data,
            context=f"create requirement '{name}'"
        )

    def update_requirement(self, requirement_id: int, name: str = None,
                           properties: List[Dict] = None,
                           project_id: int = None) -> Dict:
        """
        Update an existing requirement.

        Args:
            requirement_id: ID of requirement to update
            name: New name (optional)
            properties: List of property dicts with field_id and field_value (optional)
            project_id: Project ID (uses default if not specified)

        Returns:
            Updated requirement data
        """
        pid = project_id or self.project_id

        data = {}
        if name is not None:
            data['name'] = name
        if properties is not None:
            data['properties'] = properties

        return self._put(
            f"projects/{pid}/requirements/{requirement_id}", data,
            context=f"requirement {requirement_id}"
        )

    def delete_requirement(self, requirement_id: int, project_id: int = None) -> bool:
        """
        Delete a requirement.

        Args:
            requirement_id: ID of requirement to delete
            project_id: Project ID (uses default if not specified)

        Returns:
            True if deleted successfully
        """
        pid = project_id or self.project_id
        self._delete(f"projects/{pid}/requirements/{requirement_id}", context=f"requirement {requirement_id}")
        return True

    def get_requirement_fields(self, project_id: int = None) -> List[Dict]:
        """
        Get all available fields for requirements in this project.

        Useful for understanding what properties can be set when creating/updating.

        Args:
            project_id: Project ID (uses default if not specified)

        Returns:
            List of field definitions with id, label, attribute_type, allowed_values, etc.
        """
        pid = project_id or self.project_id
        return self._get(f"projects/{pid}/settings/requirements/fields")

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

    def get_test_runs(self, parent_id: int = None, parent_type: str = 'test-cycle',
                      project_id: int = None, page: int = 1, size: int = 100) -> List[Dict]:
        """
        Get test runs, optionally filtered by parent container.

        Args:
            parent_id: Filter by parent ID (cycle, suite, or release)
            parent_type: Type of parent - 'test-cycle', 'test-suite', 'release', or 'root'
            project_id: Project ID (uses default if not specified)
            page: Page number (1-indexed)
            size: Results per page

        Returns:
            List of test run dictionaries
        """
        pid = project_id or self.project_id
        params = {
            'page': page,
            'size': size
        }
        if parent_id:
            params['parentId'] = parent_id
            params['parentType'] = parent_type
        result = self._get(f"projects/{pid}/test-runs", params)
        # Response is paginated - return items list
        return result.get('items', result) if isinstance(result, dict) else result

    def get_test_run(self, run_id: int, project_id: int = None) -> Dict:
        """
        Get a specific test run by ID.

        Args:
            run_id: ID of the test run
            project_id: Project ID (uses default if not specified)

        Returns:
            Test run dictionary
        """
        pid = project_id or self.project_id
        return self._get(f"projects/{pid}/test-runs/{run_id}")

    def add_test_to_cycle(self, test_case_id: int, cycle_id: int,
                          name: str = None, project_id: int = None) -> Dict:
        """
        Add a test case to a test cycle by creating a test run.

        Args:
            test_case_id: ID of the test case
            cycle_id: ID of the test cycle
            name: Name for the test run (defaults to "Run-{test_case_id}")
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
        # qTest requires 'name' and 'test_case' with 'id' inside
        run_name = name or f"Run-{test_case_id}"
        data = {
            'name': run_name,
            'test_case': {'id': test_case_id}
        }
        return self._request(
            'POST', f"projects/{pid}/test-runs",
            params=params, data=data,
            context=f"add test case {test_case_id} to cycle {cycle_id}"
        )

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
            name: Name for the test run (defaults to "Run-{test_case_id}")
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

        # qTest requires 'name' and 'test_case' with 'id' inside
        run_name = name or f"Run-{test_case_id}"
        data = {
            'name': run_name,
            'test_case': {'id': test_case_id}
        }

        return self._request(
            'POST', f"projects/{pid}/test-runs",
            params=params, data=data,
            context=f"create test run for test case {test_case_id}"
        )

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

        return self._post(
            f"projects/{pid}/test-runs/{run_id}/test-logs", data,
            context=f"update test run {run_id} to '{status}'"
        )

    def get_test_logs(self, run_id: int, project_id: int = None) -> List[Dict]:
        """
        Get test logs (execution history) for a test run.

        Args:
            run_id: ID of the test run
            project_id: Project ID (uses default if not specified)

        Returns:
            List of test log dictionaries
        """
        pid = project_id or self.project_id
        result = self._get(f"projects/{pid}/test-runs/{run_id}/test-logs")
        # Response may be paginated - return items list
        return result.get('items', result) if isinstance(result, dict) else result

    # ========== Bulk Operations ==========

    def bulk_create_test_cases(self, test_cases: List[Dict], module_id: int,
                                project_id: int = None, max_workers: int = 5,
                                on_progress: Callable[[int, int, Dict], None] = None) -> Dict:
        """
        Create multiple test cases concurrently.

        Args:
            test_cases: List of dicts with keys: name, description, precondition, steps
                        steps is a list of (description, expected) tuples
            module_id: Module ID to create test cases in
            project_id: Project ID (uses default if not specified)
            max_workers: Max concurrent requests (default: 5)
            on_progress: Callback(completed, total, result) called after each creation

        Returns:
            Dict with 'succeeded' (list of created test cases) and 'failed' (list of errors)

        Example:
            test_cases = [
                {'name': 'Test 1', 'steps': [('Step 1', 'Expected 1')]},
                {'name': 'Test 2', 'description': 'Desc', 'steps': []},
            ]
            results = client.bulk_create_test_cases(test_cases, module_id=12345)
        """
        succeeded = []
        failed = []
        total = len(test_cases)

        def create_one(tc_data):
            return self.create_test_case(
                name=tc_data['name'],
                description=tc_data.get('description', ''),
                precondition=tc_data.get('precondition', ''),
                steps=tc_data.get('steps'),
                module_id=module_id,
                project_id=project_id
            )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_tc = {executor.submit(create_one, tc): tc for tc in test_cases}

            for future in as_completed(future_to_tc):
                tc_data = future_to_tc[future]
                try:
                    result = future.result()
                    succeeded.append(result)
                    if on_progress:
                        on_progress(len(succeeded) + len(failed), total, {'success': True, 'data': result})
                except Exception as e:
                    failed.append({'input': tc_data, 'error': str(e)})
                    if on_progress:
                        on_progress(len(succeeded) + len(failed), total, {'success': False, 'error': str(e)})

        return {'succeeded': succeeded, 'failed': failed}

    def bulk_link_to_requirement(self, test_case_ids: List[int], requirement_id: int,
                                  project_id: int = None) -> Dict:
        """
        Link multiple test cases to a requirement in a single API call.

        Args:
            test_case_ids: List of test case IDs to link
            requirement_id: Requirement ID to link them to
            project_id: Project ID (uses default if not specified)

        Returns:
            API response (empty dict on success)

        Note: This uses the native qTest batch endpoint for efficiency.
        """
        pid = project_id or self.project_id
        data = {
            'requirement_id': requirement_id,
            'testcase_ids': test_case_ids
        }
        return self._post(
            f"projects/{pid}/req-tc-links", data,
            context=f"link {len(test_case_ids)} test cases to requirement {requirement_id}"
        )

    def bulk_add_to_cycle(self, test_case_ids: List[int], cycle_id: int,
                           project_id: int = None, max_workers: int = 5,
                           on_progress: Callable[[int, int, Dict], None] = None) -> Dict:
        """
        Add multiple test cases to a test cycle concurrently.

        Args:
            test_case_ids: List of test case IDs to add
            cycle_id: Test cycle ID to add them to
            project_id: Project ID (uses default if not specified)
            max_workers: Max concurrent requests (default: 5)
            on_progress: Callback(completed, total, result) called after each addition

        Returns:
            Dict with 'succeeded' (list of created test runs) and 'failed' (list of errors)
        """
        succeeded = []
        failed = []
        total = len(test_case_ids)

        def add_one(tc_id):
            return self.add_test_to_cycle(tc_id, cycle_id, project_id=project_id)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_id = {executor.submit(add_one, tc_id): tc_id for tc_id in test_case_ids}

            for future in as_completed(future_to_id):
                tc_id = future_to_id[future]
                try:
                    result = future.result()
                    succeeded.append(result)
                    if on_progress:
                        on_progress(len(succeeded) + len(failed), total, {'success': True, 'data': result})
                except Exception as e:
                    failed.append({'test_case_id': tc_id, 'error': str(e)})
                    if on_progress:
                        on_progress(len(succeeded) + len(failed), total, {'success': False, 'error': str(e)})

        return {'succeeded': succeeded, 'failed': failed}

    def bulk_update_test_run_status(self, updates: List[Dict], project_id: int = None,
                                     max_workers: int = 5,
                                     on_progress: Callable[[int, int, Dict], None] = None) -> Dict:
        """
        Update multiple test run statuses concurrently.

        Args:
            updates: List of dicts with keys: run_id, status, note (optional)
            project_id: Project ID (uses default if not specified)
            max_workers: Max concurrent requests (default: 5)
            on_progress: Callback(completed, total, result) called after each update

        Returns:
            Dict with 'succeeded' (list of test logs) and 'failed' (list of errors)

        Example:
            updates = [
                {'run_id': 123, 'status': 'Passed'},
                {'run_id': 456, 'status': 'Failed', 'note': 'Bug found'},
            ]
            results = client.bulk_update_test_run_status(updates)
        """
        succeeded = []
        failed = []
        total = len(updates)

        def update_one(update):
            return self.update_test_run_status(
                run_id=update['run_id'],
                status=update['status'],
                note=update.get('note'),
                project_id=project_id
            )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_update = {executor.submit(update_one, u): u for u in updates}

            for future in as_completed(future_to_update):
                update = future_to_update[future]
                try:
                    result = future.result()
                    succeeded.append(result)
                    if on_progress:
                        on_progress(len(succeeded) + len(failed), total, {'success': True, 'data': result})
                except Exception as e:
                    failed.append({'input': update, 'error': str(e)})
                    if on_progress:
                        on_progress(len(succeeded) + len(failed), total, {'success': False, 'error': str(e)})

        return {'succeeded': succeeded, 'failed': failed}

    def bulk_delete_test_cases(self, test_case_ids: List[int], project_id: int = None,
                                max_workers: int = 5,
                                on_progress: Callable[[int, int, Dict], None] = None) -> Dict:
        """
        Delete multiple test cases concurrently.

        Args:
            test_case_ids: List of test case IDs to delete
            project_id: Project ID (uses default if not specified)
            max_workers: Max concurrent requests (default: 5)
            on_progress: Callback(completed, total, result) called after each deletion

        Returns:
            Dict with 'succeeded' (list of deleted IDs) and 'failed' (list of errors)
        """
        succeeded = []
        failed = []
        total = len(test_case_ids)

        def delete_one(tc_id):
            self.delete_test_case(tc_id, project_id=project_id)
            return tc_id

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_id = {executor.submit(delete_one, tc_id): tc_id for tc_id in test_case_ids}

            for future in as_completed(future_to_id):
                tc_id = future_to_id[future]
                try:
                    result = future.result()
                    succeeded.append(result)
                    if on_progress:
                        on_progress(len(succeeded) + len(failed), total, {'success': True, 'id': result})
                except Exception as e:
                    failed.append({'test_case_id': tc_id, 'error': str(e)})
                    if on_progress:
                        on_progress(len(succeeded) + len(failed), total, {'success': False, 'error': str(e)})

        return {'succeeded': succeeded, 'failed': failed}

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
