# qTest Concepts & Workflow

## What is qTest?

qTest Manager is a test management system that helps QA teams organize, execute, and track testing efforts. It bridges the gap between requirements (what needs to be built) and test execution (proving it works).

---

## Core Concepts

### The Object Hierarchy

```
Project
├── Requirements (imported from Jira: Epics, Stories)
├── Test Design
│   └── Test Cases (reusable test procedures)
├── Test Execution
│   └── Releases
│       └── Test Cycles
│           └── Test Runs (instances of test cases)
└── Defects (linked bugs)
```

### Key Objects Explained

**Requirements**
- Typically imported from Jira (Epics, Stories, Tasks)
- Represent what needs to be built/tested
- Example: "SPACE-101: Player Ship Movement"

**Test Cases**
- Reusable test procedures stored in the Test Design area
- Written once, executed many times across different releases/sprints
- Contains: name, description, preconditions, test steps, expected results
- Example: "Verify ship moves left when left arrow pressed"

**Test Cycles**
- Organized under Releases
- Represent a testing phase (e.g., "Sprint 5 Manual Testing", "Regression Suite")
- Groups related test execution together

**Test Runs**
- An instance of a Test Case ready to be executed
- When you add a Test Case to a Test Cycle, it creates a Test Run
- Has execution status: Not Run, Passed, Failed, Blocked, Incomplete
- Can be executed multiple times (creates Test Logs each time)

**Test Logs**
- The actual execution record
- Records who ran it, when, what the result was, any notes
- A Test Run can have multiple Test Logs (if re-executed)

---

## Example Workflow: "Space Game" Sprint

### Sprint Setup
You're QA on a "Space Game" project. Sprint 5 has 5 Jira stories to test.

### Step 1: Requirements (Already in qTest)
Jira stories are imported into qTest as Requirements:
- SPACE-101: Player Ship Movement
- SPACE-102: Asteroid Collision
- SPACE-103: Score System
- SPACE-104: Sound Effects
- SPACE-105: Pause Menu

### Step 2: Create Test Cases (Design Phase)
You write reusable Test Cases in the Test Design area:
- TC-001: Verify ship moves left
- TC-002: Verify ship moves right
- TC-003: Verify ship moves up
- TC-004: Verify ship moves down
- TC-005: Verify asteroid destroys ship on collision
- TC-006: Verify score increments when asteroid avoided
- TC-007: Verify pause menu opens with ESC key

### Step 3: Link Test Cases to Requirements
You link each Test Case to its related Requirement:
- TC-001, TC-002, TC-003, TC-004 → linked to SPACE-101 (Ship Movement)
- TC-005 → linked to SPACE-102 (Asteroid Collision)
- TC-006 → linked to SPACE-103 (Score System)
- TC-007 → linked to SPACE-105 (Pause Menu)

This provides **traceability**: you can see which requirements are covered by tests.

### Step 4: Create Test Cycle for Sprint 5
Under Release "v1.0", you create a Test Cycle named "Sprint 5 - Manual QA"

### Step 5: Add Test Cases to the Cycle
You add TC-001 through TC-007 to the "Sprint 5 - Manual QA" cycle.
This creates 7 **Test Runs** (instances ready to execute).

### Step 6: Execute Test Runs
During sprint testing, you:
1. Open each Test Run
2. Follow the steps in the Test Case
3. Mark the status: Passed, Failed, Blocked, etc.
4. Add notes if needed
5. Create a Test Log recording the execution

### Step 7: Track Progress
qTest shows you:
- Which Requirements are fully tested vs. not tested
- Which Test Runs have passed/failed
- Test execution progress (5 of 7 runs complete)
- Defects linked to failed tests

---

## Key Distinctions

| Concept | Description | Reusable? | Example |
|---------|-------------|-----------|---------|
| **Requirement** | What needs to be built | N/A | "SPACE-101: Ship Movement" |
| **Test Case** | How to test it (template) | ✅ Yes | "TC-001: Verify left movement" |
| **Test Run** | An instance ready to execute | ❌ No | Test Run #12345 for TC-001 in Sprint 5 |
| **Test Log** | Record of actual execution | ❌ No | "Executed TC-001 on 1/4/26 - Passed" |

**Think of it like:**
- Test Case = Recipe (reusable instructions)
- Test Run = Cooking session (one time you follow the recipe)
- Test Log = Your notes about how that cooking session went

---

## This Repository's Scope

### ✅ This Repo IS:
- A **Python client library** for the qTest Manager REST API
- Focused solely on **API interactions** with qTest
- Reusable across multiple projects and automation tools
- A building block for larger integrations

### ❌ This Repo IS NOT:
- A full application or end-user tool
- Jira integration (that belongs in a separate orchestration layer)
- A GUI or web interface
- Test automation framework (use for test management only)

### How to Use This Client

**Good Use Cases:**
```python
# Automation script that creates test cases from test code
from qtest_client import QTestClient

client = QTestClient()
test_case = client.create_test_case(
    name="API Test: User Login",
    steps=[("Send POST /login", "Returns 200 OK")],
    module_id=12345
)
```

```python
# Integration tool that syncs Jira → qTest
from qtest_client import QTestClient
from jira import JIRA  # Separate library

qtest = QTestClient()
jira = JIRA(...)

# Your orchestration logic here
epic = jira.get_epic("SGD-1234")
req = qtest.find_requirement_by_name("SGD-1234")
```

**For larger integrations:**
Create a separate project that uses `qtest-api-client` as a dependency and handles business logic, Jira sync, scheduling, etc.

---

## Resources

- **qTest API Docs**: https://docs.tricentis.com/qtest-saas/content/apis/overview/qtest_api_specification.htm
- **This Client's Docs**: See [CLAUDE.md](CLAUDE.md) and [example_workflow.py](../examples/example_workflow.py)
- **API Testing Sandbox**: Project ID 127166 (safe for experimentation)
- **Project README**: See [README.md](../README.md) for quick start and usage
