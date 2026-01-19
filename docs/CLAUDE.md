# CLAUDE.md - qTest API Client

## Project Purpose
Python client for qTest Manager REST API. Direct integration - no Excel imports needed.

## Current State
- ✅ Basic client working ([qtest_client.py](../qtest_client.py))
- ✅ Can create test cases with steps
- ✅ Can list projects, modules, test cases
- ✅ Successfully created test case TC-3722 via API
- ✅ Requirements/Epic linking implemented
- ✅ Releases & Test Cycles support
- ✅ Test Run execution and status updates
- ✅ Project reorganized into clean folder structure
- ✅ Full CRUD for test cases (create, read, update, delete)
- ✅ Test run listing and retrieval
- ✅ Test log (execution history) retrieval
- ✅ Full CRUD for requirements (create, read, update, delete)
- ✅ Error handling with custom exceptions and retry logic
- ✅ Bulk operations with concurrent execution and progress callbacks
- ✅ Pytest test suite (21 unit tests + 8 integration tests)

## Credentials
Stored in `.env` (gitignored):
- `QTEST_BASE_URL` - https://lingraphica.qtestnet.com
- `QTEST_BEARER_TOKEN` - Bearer token for auth
- `QTEST_DEFAULT_PROJECT_ID` - 117269 (SGD 3.0)

## Key IDs

### SGD 3.0 Project (Production - DO NOT MODIFY)
- Project ID: 117269
- Test module "Module Name": 68179830
- Other modules: DWE Notes (68164403), Automation (57221410), 3.0 (57199049)

### API Testing Project (Sandbox - Safe for Experimentation)
- Project ID: 127166
- Created: 2026-01-04
- Purpose: Dedicated sandbox for API development and testing
- **Use this project for all API testing!**

## Default Settings
- Admin Email: delliott@lingraphica.com (safe to commit to git)

---

## ✅ COMPLETED - Mega Project Integration

All requested features have been implemented and tested!

### ✅ Requirements (Epics) - DONE
- `get_requirements(project_id)` - List requirements
- `get_requirement(requirement_id)` - Get single requirement
- `create_requirement(name, parent_id)` - Create new requirement
- `update_requirement(requirement_id, name)` - Update existing requirement
- `delete_requirement(requirement_id)` - Delete a requirement
- `get_requirement_fields(project_id)` - Get available requirement fields/properties
- `find_requirement_by_name(name)` - Search for requirement by epic name/key
- `link_test_to_requirement(test_case_id, requirement_id)` - Link test to requirement

### ✅ Releases & Test Cycles - DONE
- `get_releases(project_id)` - List available releases
- `get_test_cycles(release_id)` - List test cycles in a release
- `add_test_to_cycle(test_case_id, cycle_id)` - Add test to a test cycle (creates test run)

### ✅ Test Run Execution - DONE
- `create_test_run(test_case_id, parent_id, parent_type)` - Create a test run
- `update_test_run_status(run_id, status, note)` - Mark test as passed/failed/blocked
- `get_test_runs(parent_id, parent_type)` - List test runs in a cycle/suite
- `get_test_run(run_id)` - Get single test run details
- `get_test_logs(run_id)` - Get execution history for a test run

### ✅ Test Case CRUD - DONE
- `create_test_case(name, description, steps, module_id)` - Create new test case
- `get_test_case(test_case_id)` - Get single test case
- `get_test_cases(module_id)` - List test cases
- `update_test_case(test_case_id, name, description, steps)` - Update existing test case
- `delete_test_case(test_case_id)` - Delete a test case

### API Endpoints Used
- `GET /api/v3/projects/{id}/requirements` - List requirements
- `GET /api/v3/projects/{id}/requirements/{rid}` - Get single requirement
- `POST /api/v3/projects/{id}/requirements` - Create requirement
- `PUT /api/v3/projects/{id}/requirements/{rid}` - Update requirement
- `DELETE /api/v3/projects/{id}/requirements/{rid}` - Delete requirement
- `GET /api/v3/projects/{id}/settings/requirements/fields` - Get requirement fields
- `POST /api/v3/projects/{id}/req-tc-links` - Link test cases to requirements
- `GET /api/v3/projects/{id}/releases` - List releases
- `GET /api/v3/projects/{id}/test-cycles` - List test cycles
- `POST /api/v3/projects/{id}/test-runs` - Create test runs
- `POST /api/v3/projects/{id}/test-runs/{run_id}/test-logs` - Update run status

### Usage Example
See [example_workflow.py](../examples/example_workflow.py) for a complete workflow demonstration!

---

## Session Log
- **2026-01-03**: Initial client created. Tested successfully - created TC-3722 via API.
- **2026-01-04**: Implemented all Mega Project features:
  - Requirements/Epic linking (get, find, link methods)
  - Releases & Test Cycles support (get, add to cycle)
  - Test Run execution (create, update status)
  - All methods tested and working with live API
  - Created [example_workflow.py](../examples/example_workflow.py) demonstrating full integration
  - **Created dedicated "API Testing" project (ID: 127166)** for safe experimentation
  - All future API development should use this sandbox project
  - Reorganized project into clean folder structure (docs/, examples/, tests/, scripts/)
- **2026-01-14**: Bug fixes and new methods:
  - Fixed `add_test_to_cycle()` - was returning 400 error (needed `name` + `test_case.id` format)
  - Fixed `create_test_run()` - same issue
  - Added `get_test_runs()`, `get_test_run()`, `get_test_logs()`
  - Added `update_test_case()`, `delete_test_case()`
  - Fixed paginated API responses to return `items` array
  - Pushed to GitHub: https://github.com/delliottlg/qtest-api-client
  - Closed Issue #1, updated Issue #2
- **2026-01-19**: Major enhancements (Issues #2, #3, #4):
  - Requirement CRUD: `get_requirement()`, `create_requirement()`, `update_requirement()`, `delete_requirement()`, `get_requirement_fields()`
  - Error handling: Custom exceptions (`QTestError`, `QTestNotFoundError`, `QTestAuthenticationError`, etc.)
  - Retry logic: Exponential backoff for rate limits (429) and server errors (5xx)
  - Bulk operations: `bulk_create_test_cases()`, `bulk_link_to_requirement()`, `bulk_add_to_cycle()`, `bulk_update_test_run_status()`, `bulk_delete_test_cases()`
  - Pytest test suite: 21 unit tests (mocked) + 8 integration tests (live sandbox)
  - All issues closed except #5

## GitHub Issues
- **#1** (CLOSED): Fixed add_test_to_cycle() 400 error
- **#2** (CLOSED): Requirement CRUD methods
- **#3** (CLOSED): Error handling with custom exceptions and retry logic
- **#4** (CLOSED): Bulk operations with concurrent execution
- **#5** (OPEN): Search and query improvements

## Running Tests
```bash
# Unit tests only (fast, mocked)
pytest tests/test_client.py -v

# Integration tests (live API against sandbox)
pytest tests/test_integration.py -v -m integration

# All tests
pytest tests/ -v
```
