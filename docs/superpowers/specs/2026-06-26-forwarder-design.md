# Forwarder Design

## Overview

Add a `Forwarder` class that reads attendee data from a source Pretix event, applies a YAML-defined field mapping, and writes the transformed attendees to a destination Pretix event via the orders endpoint. Supports `skip` and `update` modes for handling existing attendees. Unit tests cover all code paths; integration tests cover the full forward flow against real Pretix instances.

## Architecture

New file: `pretix_event_person_forwarder/forwarder.py`

The `Forwarder` class follows the existing class-per-resource pattern (`Events`, `Orders`, `Questions`). It takes two `APIModel` instances (source and destination), a parsed rules dict (caller loads YAML → dict), and a mode string.

```python
class Forwarder:
    def __init__(
        self,
        source_api_model: APIModel,
        dest_api_model: APIModel,
        rules: dict,
        mode: str,  # "skip" or "update"
    ): ...

    def forward_event_persons(
        self,
        source_organizer: str,
        source_event: str,
        dest_organizer: str,
        dest_event: str,
    ) -> None: ...
```

Connection config (hosts, tokens, organizers, event slugs) is passed as Python arguments — not part of the YAML rules.

## YAML Rules Format

```yaml
fields:
  attendee_name: attendee_name
  attendee_email: attendee_email
  questions:
    - source_id: 256
      dest_id: 312
    - source_id: 257
      dest_id: 313
```

The caller loads this YAML into a Python dict and passes it to `Forwarder`. The `Forwarder` does not load YAML itself.

## Data Flow

1. **Validate mode**: Raise `ValueError` immediately if mode is not `"skip"` or `"update"` — before any API calls.
2. **Read source orders**: `Orders(source_api_model).get_event_orders(source_organizer, source_event)` — returns list of orders, each with `positions` (attendees).
3. **Validate rules**: Call `Questions(dest_api_model).get_all_event_questions(dest_organizer, dest_event)` and verify every `dest_id` in the rules exists. Raise `ValueError` immediately if any are missing — before processing any attendee data.
4. **Extract attendees**: From each order position, extract `attendee_name`, `attendee_email`, and `answers` list.
5. **Read destination orders**: Fetch existing destination attendees once upfront (keyed by email) to enable skip/update checks.
6. **Map and write**: For each source attendee:
   - Apply rules to build destination payload (map field names and remap question IDs).
   - Look up email in destination attendees. Attendees with no email are always treated as new (POST).
   - If no match → POST new order to destination.
   - If match and mode `skip` → log INFO, skip.
   - If match and mode `update` → PATCH existing order position.

## Error Handling

- `ValueError`: unknown destination question ID in rules (raised upfront, before any writes).
- `ValueError`: invalid mode value.
- API errors from `httpx` propagate naturally — consistent with existing library behavior.
- Each attendee action (created / skipped / updated) logged at INFO level.

## Unit Tests (`tests/unittests/test_forwarder.py`)

Use `pytest-httpx` (already in requirements) to mock `Api.call_the_api`.

Test cases:
- Valid rules and mode — full happy path (create)
- Skip mode — existing attendee by email is skipped
- Update mode — existing attendee by email is patched
- Unknown destination question ID in rules → `ValueError`
- Invalid mode string → `ValueError`
- Rule validation runs before any write calls

## Integration Tests (`tests/integrationtest/test_forwarder.py`)

Hit real Pretix instances using env vars:
- `PRETIX_SOURCE_HOST`, `PRETIX_SOURCE_TOKEN`
- `PRETIX_DEST_HOST`, `PRETIX_DEST_TOKEN`

Test cases:
- Forward persons from source event to destination event in `skip` mode
- Forward persons from source event to destination event in `update` mode

The integration test CI workflow (`.github/workflows/integrationtest.yml`) is updated to pass the four new env vars as secrets.

## Files Changed

| File | Change |
|------|--------|
| `pretix_event_person_forwarder/forwarder.py` | New — `Forwarder` class |
| `tests/unittests/test_forwarder.py` | New — unit tests |
| `tests/integrationtest/test_forwarder.py` | New — integration tests |
| `.github/workflows/integrationtest.yml` | Updated — add new env var secrets |
