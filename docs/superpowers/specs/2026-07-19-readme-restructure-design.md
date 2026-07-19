---
name: readme-restructure
description: Restructure README.md to follow perses_api_sdk pattern for better documentation clarity
metadata:
  type: design
  date: 2026-07-19
  target: README.md
  reference: https://github.com/ZPascal/perses_api_sdk/blob/main/README.md
---

# README Restructure Design

## Overview

Restructure the pretix-event-person-forwarder README.md to follow a proven documentation pattern from the perses_api_sdk project. This improves clarity for new users, provides quick-start guidance, and establishes a professional documentation standard.

**Reference:** The perses_api_sdk README uses a clear hierarchy: overview → requirements → installation/auth → functionality → configuration → development → license. We adapt this pattern for a Pretix forwarder library.

## Current State

The existing README.md (59 lines) covers:
- Contribution guidelines
- Support/issue reporting
- Donations
- License (Apache 2.0)
- Integration Tests (detailed setup with scripts, env vars, troubleshooting)

**Strengths:** Comprehensive integration test documentation with troubleshooting
**Gaps:** No project overview, no installation instructions, no usage examples, no feature descriptions

## Proposed Structure

Nine sections in this order:

### 1. Project Overview (2-3 sentences)
What the forwarder does, who should use it, core value proposition.

**Example intro:** "The Pretix Event Person Forwarder is a Python library that enables programmatic forwarding of event, order, and question data from Pretix to external systems via HTTP. Forward attendee registrations, order updates, and survey responses to webhooks, CRM systems, or custom APIs."

### 2. Key Requirements (bullet list)
- Python 3.8 or later (from pyproject.toml)
- Running Pretix instance with HTTPS enabled
- Valid Pretix API token for authentication

### 3. Installation (bash + optional dependencies)
Standard `pip install` command with optional http2 extra dependency.

```bash
pip install pretix-event-person-forwarder
# Optional: enable HTTP/2 support
pip install pretix-event-person-forwarder[http2]
```

### 4. Quick Start (runnable code example)
Minimal working example showing forwarder instantiation and a basic operation.

```python
from pretix_event_person_forwarder import Forwarder

forwarder = Forwarder(
    api_url="https://your-pretix-instance.com/api/",
    api_token="your-api-token"
)
```

Brief explanation of next steps (e.g., "See Documentation for detailed usage").

### 5. Core Features (bullet descriptions)
- **Forwarder** - Main orchestration class that manages event, order, and question forwarding
- **Orders** - Forward order creation, modification, and payment status changes
- **Events** - Forward event data and updates
- **Questions** - Forward survey question responses and data
- **Models** - Strongly-typed data models for all request/response payloads

### 6. Configuration & Authentication (expanded section)
**Subsections:**
- **API Token** - How to obtain from Pretix admin panel
- **Connection Options** - Configurable parameters (request timeout, HTTP/2, connection pooling, retry logic, redirects)
- **URL Format** - Explain API URL format (must include `/api/` path)

### 7. Integration Tests (existing content, unchanged)
Current subsections remain:
- Quick Setup (setup-integration-tests.sh script)
- Environment Variables table (PRETIX_HOST, PRETIX_TOKEN, PRETIX_CA_BUNDLE)
- Troubleshooting (SSL errors, connection refused, etc.)
- Cleanup (docker compose commands)

### 8. Development (new section with subsections)
- **Setup** - Using `uv` for dependency management, installing dev dependencies
- **Running Tests** - Unit tests with pytest, integration tests prerequisites
- **Building Documentation** - Using mkdocs with mkdocs-material theme
- **Code Quality** - Ruff linting, coverage requirements (80% minimum)

### 9. Contributing, Support & License (consolidated)
- Contribution guidelines (open PRs, improvements, changes)
- Support (open issues for bugs/questions)
- Donations (non-profit suggestion)
- License (Apache 2.0)

## Design Rationale

**Structure follows proven pattern:** perses_api_sdk README demonstrates this flow works for Python library documentation. Reusing this pattern makes the documentation discoverable and familiar to users of both projects.

**Overview first:** Users need to immediately understand what the project does. Current README assumes knowledge.

**Quick Start before deep docs:** Developers want to try the library before reading detailed configuration. Minimal example unblocks users faster.

**Installation early:** Standard location for pip packages; users expect this.

**Configuration & Auth together:** Authentication is a configuration concern; grouping them reduces cognitive load.

**Integration Tests unchanged:** This section is already comprehensive and well-structured; keep it.

**Development section is new:** Clarifies how to contribute code, run tests, and build docs — reduces contributor friction.

## Scope

**In scope:**
- Restructure and rewrite README.md sections
- Add code examples (quick start, configuration)
- Add feature descriptions
- Add development section
- Organize in feature branch

**Out of scope:**
- Changes to actual library code
- Documentation generation (mkdocs/docs/) — only update README.md
- Adding new features to the library
- Changes to test setup beyond documentation clarity

## Success Criteria

1. README is organized into 9 clear sections in prescribed order
2. Project overview immediately answers "what is this?"
3. Quick Start example is runnable (valid imports, minimal dependencies)
4. Each feature (Forwarder, Orders, Events, Questions) is described in 1-2 sentences
5. All existing content from current README is preserved and reorganized
6. Integration test section unchanged in content, just repositioned
7. Development section guides new contributors on uv, pytest, mkdocs, ruff
8. No broken links or code examples
9. Follows perses_api_sdk structure but customized for Pretix context

## Implementation Plan Outline

1. Create feature branch (`docs/update-readme`)
2. Rewrite README.md with new sections and content
3. Verify all code examples are syntactically valid (no imports that fail)
4. Review against design for completeness
5. Open PR with clear description of changes
6. Merge after approval

## Related Memories
[[perses-api-sdk-example]] — Reference implementation in another Pascal Zimmermann project
