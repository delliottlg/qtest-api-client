"""Inspect API response structures to understand data better"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
from qtest_client import QTestClient

client = QTestClient()

print("=" * 70)
print("INSPECTING API DATA STRUCTURES")
print("=" * 70)

# Look at requirement structure
print("\n=== REQUIREMENT STRUCTURE ===")
requirements = client.get_requirements()
if requirements:
    req = requirements[0]
    print(json.dumps(req, indent=2))

# Look at release structure
print("\n=== RELEASE STRUCTURE ===")
releases = client.get_releases()
if releases:
    rel = releases[0]
    print(json.dumps(rel, indent=2))

# Look at test cycle structure
print("\n=== TEST CYCLE STRUCTURE ===")
cycles = client.get_test_cycles()
if cycles:
    cycle = cycles[0]
    print(json.dumps(cycle, indent=2))

# Look at existing test case to see if it has requirement links
print("\n=== TEST CASE STRUCTURE (checking for requirement links) ===")
test_cases = client.get_test_cases(size=1, expand_steps=False)
if test_cases:
    tc = test_cases[0]
    print(json.dumps(tc, indent=2))
