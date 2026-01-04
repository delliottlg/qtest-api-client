# qTest API Client

Python client library for qTest Manager REST API - Direct integration, no Excel needed!

## Overview

This is a **lightweight Python library** for interacting with the qTest Manager API. It provides a simple, Pythonic interface for creating test cases, linking them to requirements, managing test cycles, and more.

**This is NOT a full application** - it's a reusable library/building block for your own integrations and automation tools.

## Features

✅ **Test Case Management**
- Create test cases with steps
- List and search test cases
- Organize with modules/folders

✅ **Requirements (Epic) Management**
- List requirements (imported from Jira)
- Search requirements by name or key
- Link test cases to requirements (traceability!)

✅ **Release & Test Cycle Management**
- List releases
- Manage test cycles
- Add tests to cycles (creates test runs)

✅ **Test Execution**
- Create test runs
- Update test run status (Pass/Fail/Blocked)
- Track execution history

## Quick Start

### Installation

```bash
# Clone the repo
git clone https://github.com/yourorg/qtest-api-client.git
cd qtest-api-client

# Install dependencies
pip install -r requirements.txt

# Set up credentials
cp .env.example .env
# Edit .env with your qTest credentials
```

### Basic Usage

```python
from qtest_client import QTestClient

# Initialize (reads from .env)
client = QTestClient()

# Create a test case
test_case = client.create_test_case(
    name="User Login - Valid Credentials",
    description="Verify user can log in",
    steps=[
        ("Navigate to login page", "Login page displays"),
        ("Enter valid credentials", "User logged in")
    ],
    module_id=12345
)

# Find and link to a requirement
requirement = client.find_requirement_by_name("USER-123")
client.link_test_to_requirement(test_case['id'], requirement['id'])

# List releases
releases = client.get_releases()
print(f"Found {len(releases)} releases")
```

## Project Structure

```
qtest-api-client/
├── qtest_client.py          # Main API client library
├── requirements.txt          # Python dependencies
├── .env                      # Credentials (gitignored)
│
├── docs/                     # Documentation
│   ├── CONCEPTS.md          # qTest concepts & workflow guide
│   ├── CLAUDE.md            # Project notes & session history
│   └── qtestAPIcopy.txt     # API reference docs
│
├── examples/                 # Example usage scripts
│   ├── example_workflow.py  # Complete workflow demo
│   ├── populate_sandbox.py  # Populate test data
│   └── view_sandbox_data.py # View sandbox contents
│
├── tests/                    # Test/validation scripts
│   ├── test_new_features.py # Feature validation
│   └── test_api_testing_project.py # Sandbox verification
│
└── scripts/                  # Utility scripts
    └── create_api_testing_project.py # Setup sandbox project
```

## Configuration

Create a `.env` file with your qTest credentials:

```bash
QTEST_BASE_URL=https://yourcompany.qtestnet.com
QTEST_BEARER_TOKEN=Bearer your-token-here
QTEST_DEFAULT_PROJECT_ID=12345

# Optional: API Testing sandbox
QTEST_API_TESTING_PROJECT_ID=67890
QTEST_ADMIN_EMAIL=you@company.com
```

## Examples

See the [examples/](examples/) directory for complete working examples:

- **[example_workflow.py](examples/example_workflow.py)** - Full workflow: create test, link to requirement, add to cycle
- **[populate_sandbox.py](examples/populate_sandbox.py)** - Create sample test data
- **[view_sandbox_data.py](examples/view_sandbox_data.py)** - View current sandbox contents

## Documentation

- **[CONCEPTS.md](docs/CONCEPTS.md)** - qTest concepts, workflow, and how this library fits in
- **[CLAUDE.md](docs/CLAUDE.md)** - Project notes, features, and development history
- **qTest API Docs** - https://docs.tricentis.com/qtest-saas/content/apis/overview/qtest_api_specification.htm

## Use Cases

**Good:**
- Automation scripts that create test cases from test code
- Jira-to-qTest sync tools (use this + jira library)
- CI/CD pipelines that update test execution status
- Bulk operations (import 100s of test cases)

**Not Intended:**
- Full GUI application (this is a library)
- Complete test management system (use qTest UI for that)
- Jira integration (that logic belongs in a separate orchestration layer)

## API Testing Sandbox

Project ID `127166` is available as a safe sandbox for testing API operations without affecting production data.

```python
client = QTestClient()
# All operations in examples/ use the sandbox project
```

## Contributing

This is an internal tool. For questions or improvements, contact the QA team.

## License

Internal use only - Lingraphica

---

**Built with ❤️ for the QA team**
