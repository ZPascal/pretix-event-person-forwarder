# README Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure README.md to follow the perses_api_sdk documentation pattern, adding overview, installation, quick start, and development guidance.

**Architecture:** Complete rewrite of README.md into 9 sections (overview → requirements → installation → quick start → features → config/auth → integration tests → development → contributing). The file grows from ~59 to ~180-200 lines with better organization and code examples.

**Tech Stack:** Markdown, Python code examples

## Global Constraints

- Python 3.8+ minimum version (from pyproject.toml)
- README.md only — no changes to code, tests, or docs/
- Preserve all existing integration tests documentation
- Apache 2.0 license only
- All code examples must use valid imports from the library
- No external URLs except GitHub and docs site

---

## File Structure

**Modify:**
- `README.md` — Complete restructure into 9 sections with new content and examples

---

## Tasks

### Task 1: Create Feature Branch

**Files:**
- Branch: `docs/update-readme`

**Interfaces:**
- Produces: Feature branch ready for README changes

- [ ] **Step 1: Create feature branch**

```bash
git checkout -b docs/update-readme
```

- [ ] **Step 2: Verify branch is created**

```bash
git branch
```

Expected: Shows `docs/update-readme` as current branch

---

### Task 2: Write Sections 1-3 (Overview, Requirements, Installation)

**Files:**
- Modify: `README.md` (lines 1-25)

**Interfaces:**
- Produces: README.md with sections 1-3 complete, maintaining current line breaks

- [ ] **Step 1: Replace beginning of README.md**

```markdown
# Pretix Event Person Forwarder

The Pretix Event Person Forwarder is a Python library that enables programmatic forwarding of event, order, and question data from Pretix to external systems via HTTP. Forward attendee registrations, order updates, and survey responses to webhooks, CRM systems, or custom APIs.

## Requirements

- Python 3.8 or later
- Running Pretix instance with HTTPS enabled
- Valid Pretix API token for authentication

## Installation

Install the package via pip:

```bash
pip install pretix-event-person-forwarder
```

**Optional:** Enable HTTP/2 support:

```bash
pip install pretix-event-person-forwarder[http2]
```

## Quick Start
```

- [ ] **Step 2: Verify sections read correctly**

Open README.md and read lines 1-25. Confirm:
- Title "Pretix Event Person Forwarder" present
- Overview explains what it does (forwarding data to external systems)
- Requirements lists Python 3.8+, Pretix instance, API token
- Installation shows both standard and [http2] variants

---

### Task 3: Write Section 4 (Quick Start)

**Files:**
- Modify: `README.md` (lines 26-40)

**Interfaces:**
- Consumes: `from pretix_event_person_forwarder import Forwarder` (from library __init__.py)
- Produces: README.md section 4 with minimal runnable example

- [ ] **Step 1: Add Quick Start section**

```markdown
## Quick Start

Get started in under a minute:

```python
from pretix_event_person_forwarder import Forwarder

forwarder = Forwarder(
    api_url="https://your-pretix-instance.com/api/",
    api_token="your-api-token"
)
```

For detailed usage and advanced configuration, see the [documentation](https://zpascal.github.io/pretix-event-person-forwarder/).

## Core Features
```

- [ ] **Step 2: Verify import is valid**

The import `from pretix_event_person_forwarder import Forwarder` must exist. Check file `pretix_event_person_forwarder/__init__.py` exports Forwarder class. Confirm section reads correctly.

---

### Task 4: Write Section 5 (Core Features)

**Files:**
- Modify: `README.md` (lines 41-55)

**Interfaces:**
- Consumes: Forwarder, Orders, Events, Questions classes from library
- Produces: README.md section 5 with feature descriptions

- [ ] **Step 1: Add Core Features section**

```markdown
The library provides several key components:

- **Forwarder** — Main orchestration class that manages event, order, and question forwarding from Pretix to external systems
- **Orders** — Forward order creation, modification, and payment status changes
- **Events** — Forward event data and updates to your endpoints
- **Questions** — Forward survey question responses and collected data
- **Models** — Strongly-typed data models for all request and response payloads

## Configuration & Authentication
```

- [ ] **Step 2: Verify section is present**

Open README.md and confirm section 5 lists all five features (Forwarder, Orders, Events, Questions, Models) with brief descriptions.

---

### Task 5: Write Section 6 (Configuration & Authentication)

**Files:**
- Modify: `README.md` (lines 56-80)

**Interfaces:**
- Produces: README.md section 6 with auth and config guidance

- [ ] **Step 1: Add Configuration & Authentication section**

```markdown
### API Token

To authenticate, you need a valid Pretix API token:

1. Log in to your Pretix admin panel
2. Navigate to **Settings → API → API tokens**
3. Create a new token or use an existing one with appropriate permissions
4. Pass the token to Forwarder: `api_token="your-token-here"`

### URL Format

The API URL must include the `/api/` path:

```python
# Correct ✓
api_url = "https://your-pretix-instance.com/api/"

# Incorrect ✗
api_url = "https://your-pretix-instance.com"
```

### Connection Options

Customize connection behavior via Forwarder constructor parameters:

- `timeout` — Request timeout in seconds (default: 30)
- `http2` — Enable HTTP/2 support (requires http2 extra dependency)
- `connection_pool_size` — Simultaneous connections (default: 10)
- `retries` — Number of automatic retries on transient failures (default: 3)
- `follow_redirects` — Follow HTTP redirects (default: True)

## Integration Tests
```

- [ ] **Step 2: Verify configuration section is present**

Open README.md and confirm:
- API Token subsection explains how to get token from Pretix admin
- URL Format shows correct vs incorrect examples
- Connection Options lists timeout, http2, connection_pool_size, retries, follow_redirects

---

### Task 6: Add Section 7 (Integration Tests - Preserve Existing)

**Files:**
- Modify: `README.md` (lines 81-130)

**Interfaces:**
- Consumes: Existing integration tests content (keep unchanged)
- Produces: README.md section 7 repositioned

- [ ] **Step 1: Copy existing Integration Tests section**

From current README.md, copy the entire "Integration Tests" section (heading + Quick Setup + Environment Variables table + Troubleshooting + Cleanup) into the new README after Configuration & Authentication, without any modifications.

Expected content includes:
- "Integration Tests" heading
- "Quick Setup" subsection with setup-integration-tests.sh reference
- Environment Variables table (PRETIX_HOST, PRETIX_TOKEN, PRETIX_CA_BUNDLE)
- "Troubleshooting" subsection with SSL, connection, organizer not found, SAN issues
- "Cleanup" subsection with docker compose commands

- [ ] **Step 2: Verify content is unchanged**

Compare existing README.md Integration Tests section with new README.md section 7. Content must be identical; only position changes.

---

### Task 7: Write Section 8 (Development - New)

**Files:**
- Modify: `README.md` (lines 131-160)

**Interfaces:**
- Produces: README.md section 8 with development guidance

- [ ] **Step 1: Add Development section**

```markdown
## Development

### Setup

This project uses `uv` for dependency management. To set up a development environment:

```bash
# Install uv if not already installed
pip install uv

# Create virtual environment and install dependencies
uv sync --all-extras
```

### Running Tests

**Unit Tests:**

```bash
pytest tests/unittests
```

Coverage must be 80% or higher.

**Integration Tests:**

See the [Integration Tests](#integration-tests) section above for setup instructions. Once configured:

```bash
pytest tests/integrationtest
```

### Building Documentation

Documentation is built with mkdocs and mkdocs-material:

```bash
# Install docs dependencies
uv sync --extra docs

# Serve locally at http://localhost:8000
mkdocs serve

# Build static site
mkdocs build
```

### Code Quality

Code is linted with Ruff:

```bash
ruff check src tests
ruff format src tests
```

To automatically fix issues:

```bash
ruff check --fix src tests
ruff format src tests
```

## Contributing
```

- [ ] **Step 2: Verify Development section is present**

Open README.md and confirm:
- Setup subsection mentions `uv` and shows `uv sync --all-extras`
- Running Tests shows pytest commands for unit and integration tests
- Coverage requirement of 80% is mentioned
- Building Documentation shows mkdocs commands
- Code Quality shows Ruff check and format commands

---

### Task 8: Write Section 9 (Contributing, Support & License)

**Files:**
- Modify: `README.md` (lines 161-175)

**Interfaces:**
- Produces: README.md section 9 (consolidated from existing content)

- [ ] **Step 1: Add Contributing, Support & License section**

```markdown
If you would like to contribute something, have an improvement request, or want to make a change inside the code, please open a pull request.

## Support

If you need support, or you encounter a bug, please don't hesitate to open an issue.

## Donations

If you want to support my work, I ask you to take an unusual action inside the open source community. Donate the money to a non-profit organization like Doctors Without Borders or the Children's Cancer Aid. I will continue to build tools because I like them, and I am passionate about developing and sharing applications.

## License

This product is available under the Apache 2.0 license.
```

- [ ] **Step 2: Verify section is present and complete**

Open README.md and confirm:
- Contributing guidelines present
- Support section present
- Donations section present with non-profit suggestion
- License section states Apache 2.0

---

### Task 9: Verify All Content Matches Spec

**Files:**
- Review: `README.md`

**Interfaces:**
- Consumes: README.md (complete rewrite)
- Produces: Verification that spec requirements are met

- [ ] **Step 1: Check section count and order**

Verify README.md has exactly 9 main sections in this order:
1. Project Overview (title + intro paragraph)
2. Requirements (bullet list)
3. Installation (bash commands)
4. Quick Start (code example)
5. Core Features (5 features listed)
6. Configuration & Authentication (3 subsections)
7. Integration Tests (existing content preserved)
8. Development (4 subsections: Setup, Running Tests, Building Docs, Code Quality)
9. Contributing, Support & License (consolidated)

- [ ] **Step 2: Verify against spec success criteria**

Check each criterion from spec:
1. ✓ README organized into 9 sections in prescribed order
2. ✓ Project overview answers "what is this?" (forwarding data to external systems)
3. ✓ Quick Start example is runnable (valid Forwarder import and instantiation)
4. ✓ Each feature (Forwarder, Orders, Events, Questions, Models) described in 1-2 sentences
5. ✓ All existing content preserved (requirements, integration tests, contribution, support, donations, license)
6. ✓ Integration Tests section unchanged in content, only repositioned
7. ✓ Development section guides on uv, pytest, mkdocs, ruff
8. ✓ No broken links or code examples (verify GitHub and docs URLs work)
9. ✓ Follows perses_api_sdk structure customized for Pretix

- [ ] **Step 3: Check for typos and formatting**

Read through entire README.md once for:
- Spelling mistakes
- Broken markdown formatting
- Inconsistent capitalization
- Missing or misaligned code blocks

---

### Task 10: Commit Changes

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: Completely rewritten README.md
- Produces: Committed changes on feature branch

- [ ] **Step 1: Stage README changes**

```bash
git add README.md
```

- [ ] **Step 2: Commit with clear message**

```bash
git commit -m "docs: restructure README following perses_api_sdk pattern

- Add project overview explaining what the forwarder does
- Add installation and quick start sections with examples
- Add core features breakdown (Forwarder, Orders, Events, Questions, Models)
- Expand configuration & authentication with API token, URL format, and options
- Add development section with uv, pytest, mkdocs, ruff guidance
- Reorganize contributing, support, donations, and license sections
- Preserve all existing integration tests documentation"
```

- [ ] **Step 3: Verify commit**

```bash
git log --oneline -1
```

Expected: Shows commit with message starting "docs: restructure README"

---

### Task 11: Verify README Renders Correctly

**Files:**
- Review: `README.md`

**Interfaces:**
- Consumes: Committed README.md

- [ ] **Step 1: View rendered README locally**

Open a terminal and cat the README to visually inspect formatting:

```bash
cat README.md
```

Verify:
- All sections are clearly separated with headers
- Code blocks are properly formatted with triple backticks
- Lists are properly indented
- Links format correctly

- [ ] **Step 2: Verify on GitHub (final check)**

Once merged/pushed, navigate to:
https://github.com/ZPascal/pretix-event-person-forwarder

The README should display clearly with:
- No broken markdown
- Proper syntax highlighting in code blocks
- All sections readable and well-organized

---

## Self-Review Against Spec

**Spec Coverage:**
- ✓ Section 1: Project Overview — Task 2
- ✓ Section 2: Key Requirements — Task 2
- ✓ Section 3: Installation — Task 2
- ✓ Section 4: Quick Start — Task 3
- ✓ Section 5: Core Features — Task 4
- ✓ Section 6: Configuration & Authentication — Task 5
- ✓ Section 7: Integration Tests — Task 6
- ✓ Section 8: Development — Task 7
- ✓ Section 9: Contributing, Support & License — Task 8
- ✓ Verification & completeness check — Task 9
- ✓ Commit and integration — Tasks 10-11

**Placeholder Scan:**
- No "TBD", "TODO", "add later" found
- All code examples are complete and exact
- All steps have concrete commands with expected output
- No "similar to" references — each task is self-contained

**Type Consistency:**
- Imports: `from pretix_event_person_forwarder import Forwarder` used consistently (Task 3)
- Feature names consistent: Forwarder, Orders, Events, Questions, Models (Tasks 4, 5)
- Command formats consistent across pytest, uv, mkdocs, ruff
- Section numbers and order match spec exactly (1-9)

**No Gaps:**
- All 9 sections specified in design are implemented
- Success criteria all addressable via tasks
- Existing content preservation confirmed in Task 6
- Code example validation included in Task 3, Task 9
