"""Test script for newly implemented qTest API features"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from qtest_client import QTestClient

client = QTestClient()

print("=" * 70)
print("TESTING NEW QTEST API FEATURES")
print("=" * 70)

# Test 1: Get Requirements
print("\n[1/5] Testing get_requirements()...")
try:
    requirements = client.get_requirements()
    print(f"✓ Success! Found {len(requirements)} requirements")
    if requirements:
        print(f"  Sample: {requirements[0].get('name', 'N/A')} (ID: {requirements[0].get('id')})")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Get Releases
print("\n[2/5] Testing get_releases()...")
try:
    releases = client.get_releases()
    print(f"✓ Success! Found {len(releases)} releases")
    if releases:
        for r in releases[:3]:
            print(f"  - {r.get('name', 'N/A')} (ID: {r.get('id')})")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Get Test Cycles
print("\n[3/5] Testing get_test_cycles()...")
try:
    cycles = client.get_test_cycles()
    print(f"✓ Success! Found {len(cycles)} test cycles")
    if cycles:
        for c in cycles[:3]:
            print(f"  - {c.get('name', 'N/A')} (ID: {c.get('id')})")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Find requirement by name (if we have requirements)
print("\n[4/5] Testing find_requirement_by_name()...")
try:
    requirements = client.get_requirements()
    if requirements:
        search_term = "SGD"  # Common prefix in your Jira keys
        result = client.find_requirement_by_name(search_term)
        if result:
            print(f"✓ Success! Found: {result.get('name', 'N/A')} (ID: {result.get('id')})")
        else:
            print(f"  No requirement found matching '{search_term}'")
    else:
        print("  Skipped - no requirements available")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 5: Connection verification
print("\n[5/5] Verifying existing functionality still works...")
try:
    modules = client.get_modules()
    print(f"✓ Success! get_modules() still works ({len(modules)} modules)")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 70)
print("TESTING COMPLETE")
print("=" * 70)
