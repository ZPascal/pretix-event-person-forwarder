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
            mock_api.assert_not_called()


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
            patch_payload = json.loads(call_args[1]["json_complete"] if "json_complete" in call_args[1] else call_args[0][2])
            self.assertEqual(patch_payload["attendee_name"], "Jane Doe")
            self.assertEqual(patch_payload["attendee_email"], "jane@example.com")
            self.assertEqual(patch_payload["answers"][0]["question"], 312)
            self.assertEqual(patch_payload["answers"][0]["answer"], "Berlin")

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
