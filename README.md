# Pretix Event Person Forwarder ![Coverage report](https://github.com/ZPascal/pretix-event-person-forwarder/blob/main/docs/coverage.svg)

The Pretix Event Person Forwarder is a Python library that enables programmatic forwarding of event, order, and question data from Pretix to external systems via HTTP. Forward attendee registrations, order updates, and survey responses to webhooks, CRM systems, custom APIs or other Pretix systems.

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

The library provides several key components:

- **Forwarder** — Main orchestration class that manages event, order, and question forwarding from Pretix to external systems
- **Orders** — Forward order creation, modification, and payment status changes
- **Events** — Forward event data and updates to your endpoints
- **Questions** — Forward survey question responses and collected data
- **Models** — Strongly-typed data models for all request and response payloads

## Configuration & Authentication

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

Integration tests require a running Pretix instance with HTTPS. The easiest way to set one up locally is via [pretix-docker-compose](https://github.com/ZPascal/pretix-docker-compose), checked out as a sibling directory (`../pretix-docker-compose`).

### Quick Setup

Run the setup script to generate certificates, start Docker, and create test data:

```bash
chmod +x scripts/setup-integration-tests.sh
./scripts/setup-integration-tests.sh
```

The script prints the exact `export` commands to run before executing the tests.

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `PRETIX_HOST` | URL of the Pretix API | `https://localhost` |
| `PRETIX_TOKEN` | API token for the test user | required |
| `PRETIX_CA_BUNDLE` | Path to test CA certificate | SSL verification skipped if unset |

### Troubleshooting

**SSL: CERTIFICATE_VERIFY_FAILED** — Verify `PRETIX_CA_BUNDLE` is exported, points to an absolute path, and the file is readable.

**Connection Refused** — Check that containers are running (`docker compose ps`) and port 443 is available. Inspect logs with `docker compose logs -f pretix_app`.

**Organizer not found** — Rerun the setup script or manually execute `docker exec -i pretix_app pretix shell < tests/integrationtest/setup_testdata.py` and check for errors.

**Subject Alternative Name does not match** — Regenerate certificates. Verify SANs with:
```bash
openssl x509 -in ../pretix-docker-compose/docker/pretix/files/config/ssl/domain.crt \
  -text -noout | grep -A1 "Subject Alternative Name"
```

### Cleanup

```bash
cd ../pretix-docker-compose
docker compose down          # stop containers
docker compose down -v       # stop and remove volumes
```

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

If you would like to contribute something, have an improvement request, or want to make a change inside the code, please open a pull request.

## Support

If you need support, or you encounter a bug, please don't hesitate to open an issue.

## Donations

If you want to support my work, I ask you to take an unusual action inside the open source community. Donate the money to a non-profit organization like Doctors Without Borders or the Children's Cancer Aid. I will continue to build tools because I like them, and I am passionate about developing and sharing applications.

## License

This product is available under the Apache 2.0 license.
