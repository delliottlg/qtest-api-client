# CLAUDE.md - qTest API Client

## Project Purpose
Python client for qTest Manager REST API. Direct integration - no Excel imports needed.

## Current State
- ✅ Basic client working ([qtest_client.py](../qtest_client.py))
- ✅ Can create test cases with steps
- ✅ Can list projects, modules, test cases
- ✅ Successfully created test case TC-3722 via API
- ✅ **NEW**: Requirements/Epic linking implemented
- ✅ **NEW**: Releases & Test Cycles support
- ✅ **NEW**: Test Run execution and status updates
- ✅ **NEW**: Project reorganized into clean folder structure

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
- `find_requirement_by_name(name)` - Search for requirement by epic name/key
- `link_test_to_requirement(test_case_id, requirement_id)` - Link test to requirement

### ✅ Releases & Test Cycles - DONE
- `get_releases(project_id)` - List available releases
- `get_test_cycles(release_id)` - List test cycles in a release
- `add_test_to_cycle(test_case_id, cycle_id)` - Add test to a test cycle (creates test run)

### ✅ Test Run Execution - DONE
- `create_test_run(test_case_id, parent_id, parent_type)` - Create a test run
- `update_test_run_status(run_id, status, note)` - Mark test as passed/failed/blocked

### API Endpoints Used
- `GET /api/v3/projects/{id}/requirements` - List requirements
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
