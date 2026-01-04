"""Populate the API Testing sandbox with sample data"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from qtest_client import QTestClient

# Use the sandbox project
SANDBOX_PROJECT_ID = 127166
client = QTestClient()

print("=" * 70)
print("POPULATING API TESTING SANDBOX")
print("=" * 70)

# Step 1: Create a module for organizing test cases
print("\n[1/6] Creating test module...")
module_data = {
    'name': 'Sample Test Module',
    'description': 'Module created via API for testing'
}
module = client._post(f"projects/{SANDBOX_PROJECT_ID}/modules", module_data)
module_id = module['id']
print(f"✓ Created module: {module['name']} (ID: {module_id})")

# Step 2: Create a few test cases
print("\n[2/6] Creating test cases...")
test_cases = []

test_case_1 = client.create_test_case(
    name="User Login - Valid Credentials",
    description="Verify user can successfully log in with valid credentials",
    precondition="User account exists and is active",
    steps=[
        ("Navigate to login page", "Login page displays"),
        ("Enter valid username", "Username accepted"),
        ("Enter valid password", "Password accepted"),
        ("Click Login button", "User redirected to dashboard")
    ],
    module_id=module_id,
    project_id=SANDBOX_PROJECT_ID
)
test_cases.append(test_case_1)
print(f"✓ Created: {test_case_1['name']} (ID: {test_case_1['id']})")

test_case_2 = client.create_test_case(
    name="User Login - Invalid Password",
    description="Verify error message when invalid password is entered",
    precondition="User account exists",
    steps=[
        ("Navigate to login page", "Login page displays"),
        ("Enter valid username", "Username accepted"),
        ("Enter invalid password", "Password field shows error"),
        ("Click Login button", "Error message: 'Invalid credentials'")
    ],
    module_id=module_id,
    project_id=SANDBOX_PROJECT_ID
)
test_cases.append(test_case_2)
print(f"✓ Created: {test_case_2['name']} (ID: {test_case_2['id']})")

test_case_3 = client.create_test_case(
    name="User Profile - Update Email",
    description="Verify user can update their email address",
    precondition="User is logged in",
    steps=[
        ("Navigate to Profile Settings", "Profile page displays"),
        ("Click Edit Email button", "Email edit form appears"),
        ("Enter new valid email", "Email validated"),
        ("Click Save", "Success message displays, email updated")
    ],
    module_id=module_id,
    project_id=SANDBOX_PROJECT_ID
)
test_cases.append(test_case_3)
print(f"✓ Created: {test_case_3['name']} (ID: {test_case_3['id']})")

# Step 3: Create a requirement module (requirements use same modules endpoint)
print("\n[3/6] Creating requirement module...")
req_module_data = {
    'name': 'Requirements Module',
    'description': 'Container for requirements',
    'object_type': 'requirements'  # Specify this is for requirements
}
req_module = client._post(f"projects/{SANDBOX_PROJECT_ID}/modules", req_module_data)
req_module_id = req_module['id']
print(f"✓ Created requirement module: {req_module['name']} (ID: {req_module_id})")

# Now create requirement under the module
print("\n[4/6] Creating requirement...")
requirement_data = {
    'name': 'USER-001 User Authentication System'
}
requirement = client._post(f"projects/{SANDBOX_PROJECT_ID}/requirements?parentId={req_module_id}", requirement_data)
requirement_id = requirement['id']
print(f"✓ Created requirement: {requirement['name']} (ID: {requirement_id})")

# Step 5: Link test cases to requirement
print("\n[5/6] Linking test cases to requirement...")
for tc in test_cases[:2]:  # Link first 2 test cases to auth requirement
    link_result = client.link_test_to_requirement(tc['id'], requirement_id, SANDBOX_PROJECT_ID)
    print(f"✓ Linked TC-{tc['id']} to requirement")

# Step 6: Create a release
print("\n[6/6] Creating release...")
release_data = {
    'name': 'Version 1.0',
    'description': 'Initial release'
}
release = client._post(f"projects/{SANDBOX_PROJECT_ID}/releases", release_data)
release_id = release['id']
print(f"✓ Created release: {release['name']} (ID: {release_id})")

# Step 7: Create a test cycle under the release
print("\n[7/7] Creating test cycle...")
cycle_data = {
    'name': 'Sprint 1 - Manual Testing',
    'description': 'Manual test cycle for Sprint 1'
}
cycle = client._post(f"projects/{SANDBOX_PROJECT_ID}/test-cycles?parentId={release_id}&parentType=release", cycle_data)
cycle_id = cycle['id']
print(f"✓ Created test cycle: {cycle['name']} (ID: {cycle_id})")

# Add test cases to the cycle
print("\n[Bonus] Adding test cases to cycle...")
for tc in test_cases:
    try:
        test_run = client.add_test_to_cycle(tc['id'], cycle_id, SANDBOX_PROJECT_ID)
        print(f"✓ Added test case to cycle (Test Run ID: {test_run.get('id', 'created')})")
    except Exception as e:
        print(f"  Note: Could not add TC-{tc['id']} to cycle ({str(e)[:50]}...)")

print("\n" + "=" * 70)
print("✓ SANDBOX POPULATED SUCCESSFULLY!")
print("=" * 70)
print(f"\nCreated:")
print(f"  • 1 Test Case Module: 'Sample Test Module' (ID: {module_id})")
print(f"  • 3 Test Cases with steps")
print(f"  • 1 Requirement Module: 'Requirements Module' (ID: {req_module_id})")
print(f"  • 1 Requirement: 'USER-001' (ID: {requirement_id})")
print(f"  • 2 Test-to-Requirement Links")
print(f"  • 1 Release: 'Version 1.0' (ID: {release_id})")
print(f"  • 1 Test Cycle: 'Sprint 1' (ID: {cycle_id})")
print(f"  • 3 Test Runs in the cycle")

print(f"\nView in qTest:")
print(f"  Project: https://lingraphica.qtestnet.com/p/{SANDBOX_PROJECT_ID}")
print("=" * 70)
