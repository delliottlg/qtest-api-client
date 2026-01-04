"""View all data in the API Testing sandbox"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from qtest_client import QTestClient

SANDBOX_PROJECT_ID = 127166
client = QTestClient()

print("=" * 70)
print("API TESTING SANDBOX - DATA SUMMARY")
print("=" * 70)

# Test Cases
print("\n=== TEST CASES ===")
test_cases = client.get_test_cases(SANDBOX_PROJECT_ID, size=20, expand_steps=False)
print(f"Total: {len(test_cases)}")
for tc in test_cases[-3:]:  # Show last 3
    print(f"  [{tc['id']}] {tc['name']}")

# Requirements
print("\n=== REQUIREMENTS ===")
requirements = client.get_requirements(SANDBOX_PROJECT_ID)
print(f"Total: {len(requirements)}")
for req in requirements:
    print(f"  [{req['id']}] {req['name']}")

# Releases
print("\n=== RELEASES ===")
releases = client.get_releases(SANDBOX_PROJECT_ID)
print(f"Total: {len(releases)}")
for rel in releases:
    print(f"  [{rel['id']}] {rel['name']}")

# Modules
print("\n=== MODULES ===")
modules = client.get_modules(SANDBOX_PROJECT_ID)
print(f"Total: {len(modules)}")
for mod in modules[-3:]:  # Show last 3
    print(f"  [{mod['id']}] {mod['name']}")

print("\n" + "=" * 70)
print("View in qTest:")
print(f"  https://lingraphica.qtestnet.com/p/{SANDBOX_PROJECT_ID}")
print("=" * 70)
