"""Create a dedicated API Testing project for safe API development"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from datetime import datetime, timedelta
from qtest_client import QTestClient

client = QTestClient()

print("=" * 70)
print("Creating API Testing Project")
print("=" * 70)

# Project details
# Date format: "2015-04-24T17:00:00Z" per API docs
start_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
end_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")

project_data = {
    "name": "API Testing",
    "description": "Sandbox for API testing - safe for experimentation",
    "start_date": start_date,
    "end_date": end_date
}

print(f"\nProject details:")
print(f"  Name: {project_data['name']}")
print(f"  Description: {project_data['description']}")
print(f"\nCreating project...")

try:
    url = f"{client.api_url}/projects"
    response = client.session.post(url, json=project_data)
    print(f"\nResponse status: {response.status_code}")
    print(f"Response body: {response.text}")
    response.raise_for_status()
    result = response.json()

    print(f"\n✓ Success! Project created:")
    print(f"  Project ID: {result['id']}")
    print(f"  Name: {result['name']}")
    print(f"  URL: {result.get('links', [{}])[0].get('href', 'N/A')}")

    print(f"\n" + "=" * 70)
    print(f"NEXT STEPS:")
    print(f"  1. Update .env with: QTEST_API_TESTING_PROJECT_ID={result['id']}")
    print(f"  2. All future API tests will use this project")
    print(f"  3. Safe to create/modify/delete data here!")
    print("=" * 70)

except Exception as e:
    print(f"\n✗ Error creating project: {e}")
    print(f"\nThis might be a permissions issue - project creation may require admin rights.")
    print(f"You may need to create the project manually in the qTest UI.")
