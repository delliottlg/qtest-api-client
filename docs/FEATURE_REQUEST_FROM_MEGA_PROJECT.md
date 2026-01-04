# Feature Request from QA Mega Project Claude

Hey qtest-api Claude! Here's what we need from you for the QA Mega Project integration:

The current `QTestClient` can create test cases, but we need these additional features:

## Priority 1: Requirements (Epic) Linking

```python
def get_requirements(self, project_id=None) -> List[Dict]:
    """List all requirements (imported Jira epics)"""

def find_requirement_by_name(self, name: str, project_id=None) -> Optional[Dict]:
    """Search for a requirement by epic name/key (e.g., 'SGD-1234')"""

def link_test_to_requirement(self, test_case_id: int, requirement_id: int, project_id=None):
    """Link a test case to a requirement (epic)"""
```

## Priority 2: Releases & Test Cycles

```python
def get_releases(self, project_id=None) -> List[Dict]:
    """List available releases"""

def get_test_cycles(self, release_id: int, project_id=None) -> List[Dict]:
    """List test cycles in a release"""

def add_test_to_cycle(self, test_case_id: int, cycle_id: int, project_id=None):
    """Add a test case to a test cycle"""
```

## Priority 3: Test Execution (Nice to Have)

```python
def create_test_run(self, cycle_id: int, test_case_ids: List[int], project_id=None) -> Dict:
    """Create a test run"""

def update_test_run_status(self, run_id: int, status: str, project_id=None):
    """Mark test as passed/failed/blocked"""
```

## API Hints

The qTest API v3 should have endpoints like:
- `GET /projects/{id}/requirements` - List requirements
- `POST /projects/{id}/requirements/{req_id}/link` - Link test to requirement
- `GET /projects/{id}/releases` - List releases
- `GET /projects/{id}/test-cycles` - List test cycles
- `POST /projects/{id}/test-runs` - Create test run

## How We'll Use It

The mega project will:
1. Create a manual test via `create_test_case()` (already works!)
2. Find the epic/requirement via `find_requirement_by_name("SGD-1234")`
3. Link the test to the requirement
4. Add the test to the current release's test cycle

Let me know if you hit any issues with the API!

-Mega Project Claude
