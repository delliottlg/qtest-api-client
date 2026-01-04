"""Verify the API Testing project is accessible and ready to use"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
from qtest_client import QTestClient

# Load the new project ID
API_TESTING_PROJECT_ID = int(os.getenv('QTEST_API_TESTING_PROJECT_ID', 127166))

client = QTestClient()

print("=" * 70)
print("VERIFYING API TESTING PROJECT")
print("=" * 70)

# Get project details
print(f"\nFetching project details for ID: {API_TESTING_PROJECT_ID}")
project = client.get_project(API_TESTING_PROJECT_ID)

print(f"\n✓ Project found!")
print(f"  Name: {project['name']}")
print(f"  Description: {project.get('description', 'N/A')}")
print(f"  Start Date: {project.get('start_date', 'N/A')}")
print(f"  Automation Enabled: {project.get('automation', False)}")

# Check modules
print(f"\nChecking modules in project...")
modules = client.get_modules(API_TESTING_PROJECT_ID)
print(f"  Current modules: {len(modules)}")
if modules:
    for m in modules:
        print(f"    - {m['name']} (ID: {m['id']})")

# Check test cases
print(f"\nChecking test cases...")
test_cases = client.get_test_cases(API_TESTING_PROJECT_ID, size=10)
print(f"  Current test cases: {len(test_cases)}")

# Check requirements
print(f"\nChecking requirements...")
requirements = client.get_requirements(API_TESTING_PROJECT_ID)
print(f"  Current requirements: {len(requirements)}")

# Check releases
print(f"\nChecking releases...")
releases = client.get_releases(API_TESTING_PROJECT_ID)
print(f"  Current releases: {len(releases)}")

# Check test cycles
print(f"\nChecking test cycles...")
cycles = client.get_test_cycles(project_id=API_TESTING_PROJECT_ID)
print(f"  Current test cycles: {len(cycles)}")

print("\n" + "=" * 70)
print("✓ API Testing Project is ready!")
print("  Project ID: 127166")
print("  Safe for creating test cases, requirements, releases, etc.")
print("=" * 70)
