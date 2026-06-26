# Forwarder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `Forwarder` class that reads attendee data from a source Pretix event, maps fields via a YAML-derived rules dict, and writes attendees to a destination Pretix event, with `skip` and `update` modes for existing attendees.

**Architecture:** A single `Forwarder` class in `pretix_event_person_forwarder/forwarder.py` follows the existing class-per-resource pattern. It uses the existing `Orders` and `Questions` classes for reads and calls the Pretix orders API directly for writes. Unit tests mock `Api.call_the_api`; integration tests hit real instances via env vars.

**Tech Stack:** Python 3.10, httpx, pytest, pytest-httpx, unittest.TestCase

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `pretix_event_person_forwarder/forwarder.py` | Create | `Forwarder` class — validate, read, map, write |
| `tests/unittests/test_forwarder.py` | Create | Unit tests — all code paths mocked |
| `tests/integrationtest/test_forwarder.py` | Create | Integration tests — real Pretix instances |
| `.github/workflows/integrationtest.yml` | Modify | Add new env var secrets |

---

## Background: Pretix API Shape

The Pretix orders API returns paginated results. `get_event_orders()` already unwraps `results`. Each order looks like:

```json
{
  "code": "ABCDE",
  "positions": [
    {
      "id": 1,
      "attendee_name": "Jane Doe",
      "attendee_email": "jane@example.com",
      "answers": [
        {"question": 256, "answer": "Berlin"}
      ]
    }
  ]
}
```

To POST a new order (minimal payload):

```
POST /api/v1/organizers/{organizer}/events/{event}/orders/
{
  "positions": [
    {
      "item": <item_id>,   -- required by Pretix; use first available item from dest event
      "attendee_name": "Jane Doe",
      "attendee_email": "jane@example.com",
      "answers": [{"question": 312, "answer": "Berlin"}]
    }
  ],
  "email": "jane@example.com",
  "locale": "en",
  "sales_channel": "web",
  "payment_provider": "manual"
}
```

To PATCH an existing order position:

```
PATCH /api/v1/organizers/{organizer}/events/{event}/orders/{code}/positions/{id}/
{
  "attendee_name": "Jane Doe",
  "attendee_email": "jane@example.com",
  "answers": [{"question": 312, "answer": "Berlin"}]
}
```

The `APIEndpoints` enum is in `pretix_event_person_forwarder/model.py`. Use `Api(model).call_the_api(path, method, json_complete)` for all HTTP calls. `json_complete` must be a JSON string (`json.dumps(...)`).

---

## Task 1: Implement `Forwarder` class (TDD — write tests first)

**Files:**
- Create: `tests/unittests/test_forwarder.py`
- Create: `pretix_event_person_forwarder/forwarder.py`

### Step 1.1 — Write all failing unit tests

Create `tests/unittests/test_forwarder.py`:

```python
import json
from unittest import TestCase
from unittest.mock import patch, MagicMock

from pretix_event_person_forwarder.model import APIModel
from pretix_event_person_forwarder.forwarder import Forwarder


SOURCE_MODEL = APIModel(host="https://source.pretix.eu/", token="src-token")
DEST_MODEL = APIModel(host="https://dest.pretix.eu/", token="dst-token")

RULES = {
    "fields": {
        "attendee_name": "attendee_name",
        "attendee_email": "attendee_email",
        "questions": [
            {"source_id": 256, "dest_id": 312},
        ],
    }
}

SOURCE_ORDERS = [
    {
        "code": "AAAAA",
        "positions": [
            {
                "id": 1,
                "attendee_name": "Jane Doe",
                "attendee_email": "jane@example.com",
                "answers": [{"question": 256, "answer": "Berlin"}],
            }
        ],
    }
]

DEST_QUESTIONS = [{"id": 312, "question": {"en": "City"}}]
DEST_ORDERS_EMPTY = []
DEST_ORDERS_WITH_JANE = [
    {
        "code": "BBBBB",
        "positions": [
            {
                "id": 10,
                "attendee_name": "Jane Doe",
                "attendee_email": "jane@example.com",
                "answers": [],
            }
        ],
    }
]


class TestForwarderValidation(TestCase):
    def test_invalid_mode_raises_value_error(self):
        with self.assertRaises(ValueError):
            Forwarder(SOURCE_MODEL, DEST_MODEL, RULES, "invalid")

    def test_unknown_dest_question_id_raises_value_error(self):
        bad_rules = {
            "fields": {
                "questions": [{"source_id": 256, "dest_id": 999}]
            }
        }
        forwarder = Forwarder(SOURCE_MODEL, DEST_MODEL, bad_rules, "skip")
        with patch(
            "pretix_event_person_forwarder.forwarder.Questions.get_all_event_questions",
            return_value=[{"id": 312}],
        ):
            with self.assertRaises(ValueError):
                forwarder.forward_event_persons(
                    "src-org", "src-event", "dst-org", "dst-event"
                )

    def test_rule_validation_runs_before_writes(self):
        bad_rules = {
            "fields": {
                "questions": [{"source_id": 256, "dest_id": 999}]
            }
        }
        forwarder = Forwarder(SOURCE_MODEL, DEST_MODEL, bad_rules, "skip")
        with patch(
            "pretix_event_person_forwarder.forwarder.Questions.get_all_event_questions",
            return_value=[{"id": 312}],
        ), patch(
            "pretix_event_person_forwarder.forwarder.Api.call_the_api"
        ) as mock_api:
            with self.assertRaises(ValueError):
                forwarder.forward_event_persons(
                    "src-org", "src-event", "dst-org", "dst-event"
                )
            # No POST or PATCH should have been called
            for call in mock_api.call_args_list:
                method_arg = call[1].get("method") or (call[0][1] if len(call[0]) > 1 else None)
                self.assertIsNone(method_arg)


class TestForwarderCreateMode(TestCase):
    def setUp(self):
        self.forwarder = Forwarder(SOURCE_MODEL, DEST_MODEL, RULES, "skip")

    def test_new_attendee_is_posted(self):
        with patch(
            "pretix_event_person_forwarder.forwarder.Orders.get_event_orders",
            side_effect=[SOURCE_ORDERS, DEST_ORDERS_EMPTY],
        ), patch(
            "pretix_event_person_forwarder.forwarder.Questions.get_all_event_questions",
            return_value=DEST_QUESTIONS,
        ), patch(
            "pretix_event_person_forwarder.forwarder.Api.call_the_api",
            return_value={"code": "CCCCC"},
        ) as mock_api:
            self.forwarder.forward_event_persons(
                "src-org", "src-event", "dst-org", "dst-event"
            )
            mock_api.assert_called_once()
            call_kwargs = mock_api.call_args
            posted = json.loads(call_kwargs[1]["json_complete"] if "json_complete" in call_kwargs[1] else call_kwargs[0][2])
            self.assertEqual(posted["positions"][0]["attendee_name"], "Jane Doe")
            self.assertEqual(posted["positions"][0]["attendee_email"], "jane@example.com")
            self.assertEqual(posted["positions"][0]["answers"][0]["question"], 312)
            self.assertEqual(posted["positions"][0]["answers"][0]["answer"], "Berlin")


class TestForwarderSkipMode(TestCase):
    def setUp(self):
        self.forwarder = Forwarder(SOURCE_MODEL, DEST_MODEL, RULES, "skip")

    def test_existing_attendee_is_skipped(self):
        with patch(
            "pretix_event_person_forwarder.forwarder.Orders.get_event_orders",
            side_effect=[SOURCE_ORDERS, DEST_ORDERS_WITH_JANE],
        ), patch(
            "pretix_event_person_forwarder.forwarder.Questions.get_all_event_questions",
            return_value=DEST_QUESTIONS,
        ), patch(
            "pretix_event_person_forwarder.forwarder.Api.call_the_api"
        ) as mock_api:
            self.forwarder.forward_event_persons(
                "src-org", "src-event", "dst-org", "dst-event"
            )
            mock_api.assert_not_called()


class TestForwarderUpdateMode(TestCase):
    def setUp(self):
        self.forwarder = Forwarder(SOURCE_MODEL, DEST_MODEL, RULES, "update")

    def test_existing_attendee_is_patched(self):
        with patch(
            "pretix_event_person_forwarder.forwarder.Orders.get_event_orders",
            side_effect=[SOURCE_ORDERS, DEST_ORDERS_WITH_JANE],
        ), patch(
            "pretix_event_person_forwarder.forwarder.Questions.get_all_event_questions",
            return_value=DEST_QUESTIONS,
        ), patch(
            "pretix_event_person_forwarder.forwarder.Api.call_the_api",
            return_value={},
        ) as mock_api:
            self.forwarder.forward_event_persons(
                "src-org", "src-event", "dst-org", "dst-event"
            )
            mock_api.assert_called_once()
            call_args = mock_api.call_args
            # PATCH path should include order code and position id
            path_arg = call_args[0][0] if call_args[0] else call_args[1].get("api_call")
            self.assertIn("BBBBB", path_arg)
            self.assertIn("10", path_arg)

    def test_no_email_attendee_is_always_posted(self):
        source_orders_no_email = [
            {
                "code": "CCCCC",
                "positions": [
                    {
                        "id": 2,
                        "attendee_name": "No Email",
                        "attendee_email": None,
                        "answers": [],
                    }
                ],
            }
        ]
        with patch(
            "pretix_event_person_forwarder.forwarder.Orders.get_event_orders",
            side_effect=[source_orders_no_email, DEST_ORDERS_WITH_JANE],
        ), patch(
            "pretix_event_person_forwarder.forwarder.Questions.get_all_event_questions",
            return_value=DEST_QUESTIONS,
        ), patch(
            "pretix_event_person_forwarder.forwarder.Api.call_the_api",
            return_value={"code": "DDDDD"},
        ) as mock_api:
            rules_no_questions = {"fields": {"attendee_name": "attendee_name", "attendee_email": "attendee_email", "questions": []}}
            forwarder = Forwarder(SOURCE_MODEL, DEST_MODEL, rules_no_questions, "update")
            forwarder.forward_event_persons(
                "src-org", "src-event", "dst-org", "dst-event"
            )
            mock_api.assert_called_once()
            call_args = mock_api.call_args
            path_arg = call_args[0][0] if call_args[0] else call_args[1].get("api_call")
            # Should be a POST (no order code/position in path)
            self.assertNotIn("BBBBB", path_arg)
```

- [ ] **Step 1.2 — Run tests to verify they all fail**

```bash
cd /Users/I539231/Projects/Workspaces/Upstream/pretix-event-person-forwarder
python3 -m pytest tests/unittests/test_forwarder.py -v
```

Expected: `ImportError: cannot import name 'Forwarder'` (or similar — the module doesn't exist yet).

- [ ] **Step 1.3 — Implement `Forwarder`**

Create `pretix_event_person_forwarder/forwarder.py`:

```python
import json
import logging

from .api import Api
from .model import APIModel, APIEndpoints, RequestsMethods
from .orders import Orders
from .questions import Questions


class Forwarder:
    def __init__(
        self,
        source_api_model: APIModel,
        dest_api_model: APIModel,
        rules: dict,
        mode: str,
    ):
        if mode not in ("skip", "update"):
            raise ValueError(f"Invalid mode '{mode}'. Must be 'skip' or 'update'.")
        self.source_api_model = source_api_model
        self.dest_api_model = dest_api_model
        self.rules = rules
        self.mode = mode

    def forward_event_persons(
        self,
        source_organizer: str,
        source_event: str,
        dest_organizer: str,
        dest_event: str,
    ) -> None:
        dest_question_ids = {
            q["id"]
            for q in Questions(self.dest_api_model).get_all_event_questions(
                dest_organizer, dest_event
            )
        }
        for mapping in self.rules.get("fields", {}).get("questions", []):
            if mapping["dest_id"] not in dest_question_ids:
                raise ValueError(
                    f"Destination question ID {mapping['dest_id']} not found in event '{dest_event}'."
                )

        source_orders = Orders(self.source_api_model).get_event_orders(
            source_organizer, source_event
        )
        dest_orders = Orders(self.dest_api_model).get_event_orders(
            dest_organizer, dest_event
        )

        dest_by_email: dict = {}
        for order in dest_orders:
            for position in order.get("positions", []):
                email = position.get("attendee_email")
                if email:
                    dest_by_email[email] = {"order_code": order["code"], "position_id": position["id"]}

        question_map = {
            m["source_id"]: m["dest_id"]
            for m in self.rules.get("fields", {}).get("questions", [])
        }

        for order in source_orders:
            for position in order.get("positions", []):
                self._process_position(
                    position, dest_organizer, dest_event, dest_by_email, question_map
                )

    def _process_position(
        self,
        position: dict,
        dest_organizer: str,
        dest_event: str,
        dest_by_email: dict,
        question_map: dict,
    ) -> None:
        email = position.get("attendee_email")
        mapped_answers = [
            {"question": question_map[a["question"]], "answer": a["answer"]}
            for a in position.get("answers", [])
            if a["question"] in question_map
        ]

        if email and email in dest_by_email:
            if self.mode == "skip":
                logging.info(f"Skipping existing attendee: {email}")
                return
            ref = dest_by_email[email]
            payload = {
                "attendee_name": position.get("attendee_name"),
                "attendee_email": email,
                "answers": mapped_answers,
            }
            Api(self.dest_api_model).call_the_api(
                f"{APIEndpoints.ORGANIZERS.value}/{dest_organizer}/{APIEndpoints.EVENTS.value}"
                f"/{dest_event}/{APIEndpoints.ORDERS.value}/{ref['order_code']}"
                f"/positions/{ref['position_id']}/",
                method=RequestsMethods.PATCH,
                json_complete=json.dumps(payload),
            )
            logging.info(f"Updated attendee: {email}")
        else:
            payload = {
                "positions": [
                    {
                        "attendee_name": position.get("attendee_name"),
                        "attendee_email": email,
                        "answers": mapped_answers,
                    }
                ],
                "email": email or "",
                "locale": "en",
                "sales_channel": "web",
                "payment_provider": "manual",
            }
            Api(self.dest_api_model).call_the_api(
                f"{APIEndpoints.ORGANIZERS.value}/{dest_organizer}/{APIEndpoints.EVENTS.value}"
                f"/{dest_event}/{APIEndpoints.ORDERS.value}/",
                method=RequestsMethods.POST,
                json_complete=json.dumps(payload),
            )
            logging.info(f"Created attendee: {email}")
```

- [ ] **Step 1.4 — Run all unit tests and verify they pass**

```bash
python3 -m pytest tests/unittests/test_forwarder.py -v
```

Expected output: all tests PASS. If any fail, fix the implementation until they do before continuing.

- [ ] **Step 1.5 — Commit**

```bash
git add pretix_event_person_forwarder/forwarder.py tests/unittests/test_forwarder.py
git commit -m "feat: Add Forwarder class with unit tests"
```

---

## Task 2: Integration tests for `Forwarder`

**Files:**
- Create: `tests/integrationtest/test_forwarder.py`
- Modify: `.github/workflows/integrationtest.yml`

The integration tests require four env vars pointing to two real Pretix instances:
- `PRETIX_SOURCE_HOST` / `PRETIX_SOURCE_TOKEN` — source instance
- `PRETIX_DEST_HOST` / `PRETIX_DEST_TOKEN` — destination instance
- `PRETIX_SOURCE_ORGANIZER`, `PRETIX_SOURCE_EVENT` — source event slug
- `PRETIX_DEST_ORGANIZER`, `PRETIX_DEST_EVENT` — destination event slug
- `PRETIX_FORWARDER_RULES` — JSON string of the rules dict (so it can be passed as a single env var)

These tests verify the full pipeline runs without error against real data. They do not assert exact attendee counts because the destination event state is not controlled in CI.

- [ ] **Step 2.1 — Create integration test file**

Create `tests/integrationtest/test_forwarder.py`:

```python
import json
import os
from unittest import TestCase

from pretix_event_person_forwarder.model import APIModel
from pretix_event_person_forwarder.forwarder import Forwarder


class ForwarderIntegrationTest(TestCase):
    source_model: APIModel = APIModel(
        host=os.environ["PRETIX_SOURCE_HOST"],
        token=os.environ["PRETIX_SOURCE_TOKEN"],
        http2_support=False,
        timeout=30.0,
    )
    dest_model: APIModel = APIModel(
        host=os.environ["PRETIX_DEST_HOST"],
        token=os.environ["PRETIX_DEST_TOKEN"],
        http2_support=False,
        timeout=30.0,
    )
    rules: dict = json.loads(os.environ["PRETIX_FORWARDER_RULES"])
    source_organizer: str = os.environ["PRETIX_SOURCE_ORGANIZER"]
    source_event: str = os.environ["PRETIX_SOURCE_EVENT"]
    dest_organizer: str = os.environ["PRETIX_DEST_ORGANIZER"]
    dest_event: str = os.environ["PRETIX_DEST_EVENT"]

    def test_a_forward_persons_skip_mode(self):
        forwarder = Forwarder(
            self.source_model, self.dest_model, self.rules, "skip"
        )
        forwarder.forward_event_persons(
            self.source_organizer,
            self.source_event,
            self.dest_organizer,
            self.dest_event,
        )

    def test_b_forward_persons_update_mode(self):
        forwarder = Forwarder(
            self.source_model, self.dest_model, self.rules, "update"
        )
        forwarder.forward_event_persons(
            self.source_organizer,
            self.source_event,
            self.dest_organizer,
            self.dest_event,
        )
```

- [ ] **Step 2.2 — Update CI workflow to pass new env vars**

Open `.github/workflows/integrationtest.yml`. After the existing `Execute the integrationtests (http1.1)` step, the env vars need to be available. Add `env:` to both integration test run steps.

Replace the two `run: python3 -m unittest discover tests/integrationtest` steps with:

```yaml
      - name: Execute the integrationtests (http1.1)
        run: python3 -m unittest discover tests/integrationtest
        env:
          PRETIX_HOST: ${{ secrets.PRETIX_HOST }}
          PRETIX_TOKEN: ${{ secrets.PRETIX_TOKEN }}
          PRETIX_SOURCE_HOST: ${{ secrets.PRETIX_SOURCE_HOST }}
          PRETIX_SOURCE_TOKEN: ${{ secrets.PRETIX_SOURCE_TOKEN }}
          PRETIX_DEST_HOST: ${{ secrets.PRETIX_DEST_HOST }}
          PRETIX_DEST_TOKEN: ${{ secrets.PRETIX_DEST_TOKEN }}
          PRETIX_SOURCE_ORGANIZER: ${{ secrets.PRETIX_SOURCE_ORGANIZER }}
          PRETIX_SOURCE_EVENT: ${{ secrets.PRETIX_SOURCE_EVENT }}
          PRETIX_DEST_ORGANIZER: ${{ secrets.PRETIX_DEST_ORGANIZER }}
          PRETIX_DEST_EVENT: ${{ secrets.PRETIX_DEST_EVENT }}
          PRETIX_FORWARDER_RULES: ${{ secrets.PRETIX_FORWARDER_RULES }}

      - name: Wait 20 seconds
        run: sleep 20

      - name: Execute the integrationtests (http2)
        run: python3 -m unittest discover tests/integrationtest
        env:
          PRETIX_HOST: ${{ secrets.PRETIX_HOST }}
          PRETIX_TOKEN: ${{ secrets.PRETIX_TOKEN }}
          PRETIX_SOURCE_HOST: ${{ secrets.PRETIX_SOURCE_HOST }}
          PRETIX_SOURCE_TOKEN: ${{ secrets.PRETIX_SOURCE_TOKEN }}
          PRETIX_DEST_HOST: ${{ secrets.PRETIX_DEST_HOST }}
          PRETIX_DEST_TOKEN: ${{ secrets.PRETIX_DEST_TOKEN }}
          PRETIX_SOURCE_ORGANIZER: ${{ secrets.PRETIX_SOURCE_ORGANIZER }}
          PRETIX_SOURCE_EVENT: ${{ secrets.PRETIX_SOURCE_EVENT }}
          PRETIX_DEST_ORGANIZER: ${{ secrets.PRETIX_DEST_ORGANIZER }}
          PRETIX_DEST_EVENT: ${{ secrets.PRETIX_DEST_EVENT }}
          PRETIX_FORWARDER_RULES: ${{ secrets.PRETIX_FORWARDER_RULES }}
```

Note: The existing integration tests for `Events`, `Orders`, `Questions` use `PRETIX_HOST` and `PRETIX_TOKEN` directly (as seen in `tests/integrationtest/test_events.py`). The CI workflow currently does NOT set these as `env:` on the run step — they are presumably available as repo secrets already injected into the environment. Verify this before assuming — if they are not set, the existing tests would also be broken. The new `env:` block above explicitly sets all required vars for both old and new tests.

- [ ] **Step 2.3 — Commit**

```bash
git add tests/integrationtest/test_forwarder.py .github/workflows/integrationtest.yml
git commit -m "feat: Add Forwarder integration tests and update CI workflow"
```

---

## Self-Review

**Spec coverage:**

| Spec requirement | Covered by |
|---|---|
| `Forwarder` class with two `APIModel`s, `rules`, `mode` | Task 1 step 1.3 |
| `forward_event_persons(src_org, src_event, dst_org, dst_event)` | Task 1 step 1.3 |
| Validate mode before any API calls | Task 1 step 1.3 (`__init__` raises immediately) |
| Validate dest question IDs, raise `ValueError` | Task 1 step 1.3 |
| Validate before any writes | Task 1 unit test `test_rule_validation_runs_before_writes` |
| Extract attendees from order positions | Task 1 step 1.3 `_process_position` |
| Map question IDs via rules | Task 1 step 1.3 `question_map` |
| Skip mode — existing attendee skipped | Task 1 unit test `TestForwarderSkipMode` |
| Update mode — existing attendee PATCHed | Task 1 unit test `TestForwarderUpdateMode` |
| No email → always POST | Task 1 unit test `test_no_email_attendee_is_always_posted` |
| INFO logging per action | Task 1 step 1.3 |
| httpx errors propagate naturally | No extra handling added — inherits from `Api` |
| Integration test skip mode | Task 2 step 2.1 `test_a_forward_persons_skip_mode` |
| Integration test update mode | Task 2 step 2.1 `test_b_forward_persons_update_mode` |
| CI workflow updated with new secrets | Task 2 step 2.2 |

**Placeholder scan:** None found. All steps contain exact code and commands.

**Type consistency:** `Forwarder.__init__` signature matches what unit tests instantiate. `forward_event_persons` signature matches all call sites. `_process_position` is internal and called only from `forward_event_persons`. `question_map` built in `forward_event_persons`, passed to `_process_position` — consistent.
