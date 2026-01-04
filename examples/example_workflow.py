"""
Example workflow showing how to use the qTest API client with Mega Project integration.

This demonstrates the complete workflow:
1. Create a test case
2. Link it to a requirement (Jira epic)
3. Add it to a test cycle
4. Execute and update status
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from qtest_client import QTestClient

# Initialize client
client = QTestClient()

print("=" * 70)
print("QTEST API CLIENT - MEGA PROJECT WORKFLOW EXAMPLE")
print("=" * 70)

# ============================================================================
# STEP 1: Create a Test Case
# ============================================================================
print("\n[Step 1] Creating a test case...")

# Find the module to put it in
module = client.find_module_by_name("Module Name")
if not module:
    print("✗ Module not found!")
    exit(1)

print(f"  Found module: {module['name']} (ID: {module['id']})")

# NOTE: Commented out to avoid creating test cases during demonstration
# test_case = client.create_test_case(
#     name="Example: User Login Test",
#     description="Verify user can log in with valid credentials",
#     precondition="User account exists in the system",
#     steps=[
#         ("Navigate to login page", "Login page is displayed"),
#         ("Enter valid username and password", "Credentials are accepted"),
#         ("Click login button", "User is logged in and redirected to dashboard")
#     ],
#     module_id=module['id']
# )
# print(f"✓ Created test case: {test_case['name']} (ID: {test_case['id']})")

# For demonstration, use an existing test case
test_case_id = 116595851  # Existing test case from your project
print(f"  Using existing test case ID: {test_case_id}")

# ============================================================================
# STEP 2: Link Test Case to Requirement (Epic)
# ============================================================================
print("\n[Step 2] Linking test case to requirement...")

# Find a requirement by Jira key or name
requirement = client.find_requirement_by_name("CAM")
if requirement:
    print(f"  Found requirement: {requirement['name']}")
    print(f"  Requirement ID: {requirement['id']}")
    print(f"  PID: {requirement.get('pid', 'N/A')}")

    # Link test to requirement
    # NOTE: Commented out to avoid modifying data during demonstration
    # link_result = client.link_test_to_requirement(test_case_id, requirement['id'])
    # print(f"✓ Linked test case to requirement")
    print("  (Link operation commented out for demo)")
else:
    print("  No requirement found matching 'CAM'")

# ============================================================================
# STEP 3: Add Test Case to a Release Cycle
# ============================================================================
print("\n[Step 3] Adding test case to a test cycle...")

# Get releases
releases = client.get_releases()
print(f"  Found {len(releases)} releases")
if releases:
    latest_release = releases[0]
    print(f"  Latest release: {latest_release['name']} (ID: {latest_release['id']})")

# Get test cycles
cycles = client.get_test_cycles()
print(f"  Found {len(cycles)} test cycles")
if cycles:
    target_cycle = cycles[0]
    print(f"  Target cycle: {target_cycle['name']} (ID: {target_cycle['id']})")

    # Add test to cycle (creates a test run)
    # NOTE: Commented out to avoid creating test runs during demonstration
    # test_run = client.add_test_to_cycle(test_case_id, target_cycle['id'])
    # print(f"✓ Added test to cycle (Test Run ID: {test_run['id']})")
    print("  (Add to cycle operation commented out for demo)")

# ============================================================================
# STEP 4: Create Test Run and Update Status (Optional)
# ============================================================================
print("\n[Step 4] Test execution workflow...")

# Create a test run
# NOTE: Commented out to avoid creating test runs during demonstration
# test_run = client.create_test_run(
#     test_case_id=test_case_id,
#     parent_type='root',  # or 'test-cycle', 'release', 'test-suite'
#     name="Manual Test Run - 2026-01-04"
# )
# print(f"✓ Created test run: {test_run['name']} (ID: {test_run['id']})")

# Update test run status
# test_log = client.update_test_run_status(
#     run_id=test_run['id'],
#     status='Passed',  # or 'Failed', 'Blocked', 'Incomplete'
#     note='All steps executed successfully'
# )
# print(f"✓ Updated test run status to: {test_log['status']}")
print("  (Test run creation and status update commented out for demo)")

# ============================================================================
# Summary of Available Methods
# ============================================================================
print("\n" + "=" * 70)
print("AVAILABLE METHODS SUMMARY")
print("=" * 70)

methods = """
Requirements (Epics):
  • get_requirements() - List all requirements
  • find_requirement_by_name(name) - Search for requirement by name/key
  • link_test_to_requirement(test_id, req_id) - Link test to requirement

Releases & Test Cycles:
  • get_releases() - List all releases
  • get_test_cycles(release_id) - List test cycles
  • add_test_to_cycle(test_id, cycle_id) - Add test to cycle

Test Execution:
  • create_test_run(test_case_id, parent_id, parent_type) - Create test run
  • update_test_run_status(run_id, status, note) - Update run status

Already Available:
  • create_test_case(name, description, steps, module_id) - Create test
  • get_test_cases() - List test cases
  • get_modules() - List modules/folders
  • find_module_by_name(name) - Search for module
"""

print(methods)

print("\n✓ Workflow example complete!")
print("  Uncomment the code to actually execute these operations.")
print("=" * 70)
