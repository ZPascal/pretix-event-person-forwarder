import json
from unittest import TestCase
from unittest.mock import patch

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
DEST_ITEMS = {"results": [{"id": 99, "name": {"en": "Ticket"}}]}
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
DEST_ORDERS_WITH_DUPLICATE_EMAIL = [
    {
        "code": "BBBBB",
        "positions": [
            {
                "id": 10,
                "attendee_name": "Jane Doe",
                "attendee_email": "jane@example.com",
                "answers": [],
            },
            {
                "id": 11,
                "attendee_name": "Jane Doe 2",
                "attendee_email": "jane@example.com",
                "answers": [],
            },
        ],
    }
]
DEST_ORDERS_WITH_NO_EMAIL = [
    {
        "code": "CCCC",
        "positions": [
            {
                "id": 20,
                "attendee_name": "No Email",
                "attendee_email": None,
                "answers": [],
            }
        ],
    }
]
DEST_ITEMS_EMPTY = {"results": []}


class TestForwarderValidation(TestCase):
    def test_invalid_mode_raises_value_error(self):
        with self.assertRaises(ValueError):
            Forwarder(SOURCE_MODEL, DEST_MODEL, RULES, "invalid")

    @patch(
        "pretix_event_person_forwarder.forwarder.Questions.get_all_event_questions",
        return_value=[{"id": 312}],
    )
    def test_unknown_dest_question_id_raises_value_error(self, mock_questions):
        bad_rules = {"fields": {"questions": [{"source_id": 256, "dest_id": 999}]}}
        forwarder = Forwarder(SOURCE_MODEL, DEST_MODEL, bad_rules, "skip")
        with self.assertRaises(ValueError):
            forwarder.forward_event_persons("src-org", "src-event", "dst-org", "dst-event")

    @patch(
        "pretix_event_person_forwarder.forwarder.Api.call_the_api",
        return_value=DEST_ITEMS_EMPTY,
    )
    @patch(
        "pretix_event_person_forwarder.forwarder.Questions.get_all_event_questions",
        return_value=DEST_QUESTIONS,
    )
    def test_no_items_in_destination_raises_value_error(self, mock_questions, mock_api):
        forwarder = Forwarder(SOURCE_MODEL, DEST_MODEL, RULES, "skip")
        with self.assertRaises(ValueError) as context:
            forwarder.forward_event_persons("src-org", "src-event", "dst-org", "dst-event")
        self.assertIn("No items found", str(context.exception))

    @patch("pretix_event_person_forwarder.forwarder.Api.call_the_api")
    @patch(
        "pretix_event_person_forwarder.forwarder.Questions.get_all_event_questions",
        return_value=[{"id": 312}],
    )
    def test_rule_validation_runs_before_writes(self, mock_questions, mock_api):
        bad_rules = {"fields": {"questions": [{"source_id": 256, "dest_id": 999}]}}
        forwarder = Forwarder(SOURCE_MODEL, DEST_MODEL, bad_rules, "skip")
        with self.assertRaises(ValueError):
            forwarder.forward_event_persons("src-org", "src-event", "dst-org", "dst-event")
        mock_api.assert_not_called()


class TestForwarderCreateMode(TestCase):
    def setUp(self):
        self.forwarder = Forwarder(SOURCE_MODEL, DEST_MODEL, RULES, "skip")

    @patch(
        "pretix_event_person_forwarder.forwarder.Api.call_the_api",
        side_effect=[DEST_ITEMS, {"code": "CCCCC"}],
    )
    @patch(
        "pretix_event_person_forwarder.forwarder.Questions.get_all_event_questions",
        return_value=DEST_QUESTIONS,
    )
    @patch(
        "pretix_event_person_forwarder.forwarder.Orders.get_event_orders",
        side_effect=[SOURCE_ORDERS, DEST_ORDERS_EMPTY],
    )
    def test_new_attendee_is_posted(self, mock_orders, mock_questions, mock_api):
        self.forwarder.forward_event_persons("src-org", "src-event", "dst-org", "dst-event")
        self.assertEqual(mock_api.call_count, 2)
        post_call = mock_api.call_args_list[1]
        posted = json.loads(post_call[1]["json_complete"])
        self.assertEqual(posted["positions"][0]["item"], 99)
        self.assertEqual(posted["positions"][0]["attendee_name"], "Jane Doe")
        self.assertEqual(posted["positions"][0]["attendee_email"], "jane@example.com")
        self.assertEqual(posted["positions"][0]["answers"][0]["question"], 312)
        self.assertEqual(posted["positions"][0]["answers"][0]["answer"], "Berlin")


class TestForwarderSkipMode(TestCase):
    def setUp(self):
        self.forwarder = Forwarder(SOURCE_MODEL, DEST_MODEL, RULES, "skip")

    @patch(
        "pretix_event_person_forwarder.forwarder.Api.call_the_api",
        return_value=DEST_ITEMS,
    )
    @patch(
        "pretix_event_person_forwarder.forwarder.Questions.get_all_event_questions",
        return_value=DEST_QUESTIONS,
    )
    @patch(
        "pretix_event_person_forwarder.forwarder.Orders.get_event_orders",
        side_effect=[SOURCE_ORDERS, DEST_ORDERS_WITH_JANE],
    )
    def test_existing_attendee_is_skipped(self, mock_orders, mock_questions, mock_api):
        self.forwarder.forward_event_persons("src-org", "src-event", "dst-org", "dst-event")
        self.assertEqual(mock_api.call_count, 1)
        self.assertNotIn("json_complete", mock_api.call_args[1])


class TestForwarderUpdateMode(TestCase):
    def setUp(self):
        self.forwarder = Forwarder(SOURCE_MODEL, DEST_MODEL, RULES, "update")

    @patch(
        "pretix_event_person_forwarder.forwarder.Api.call_the_api",
        side_effect=[DEST_ITEMS, {}],
    )
    @patch(
        "pretix_event_person_forwarder.forwarder.Questions.get_all_event_questions",
        return_value=DEST_QUESTIONS,
    )
    @patch(
        "pretix_event_person_forwarder.forwarder.Orders.get_event_orders",
        side_effect=[SOURCE_ORDERS, DEST_ORDERS_WITH_JANE],
    )
    def test_existing_attendee_is_patched(self, mock_orders, mock_questions, mock_api):
        self.forwarder.forward_event_persons("src-org", "src-event", "dst-org", "dst-event")
        self.assertEqual(mock_api.call_count, 2)
        patch_call = mock_api.call_args_list[1]
        path_arg = patch_call[0][0]
        self.assertIn("BBBBB", path_arg)
        self.assertIn("10", path_arg)
        patch_payload = json.loads(patch_call[1]["json_complete"])
        self.assertEqual(patch_payload["attendee_name"], "Jane Doe")
        self.assertEqual(patch_payload["attendee_email"], "jane@example.com")
        self.assertEqual(patch_payload["answers"][0]["question"], 312)
        self.assertEqual(patch_payload["answers"][0]["answer"], "Berlin")

    @patch(
        "pretix_event_person_forwarder.forwarder.Api.call_the_api",
        side_effect=[DEST_ITEMS, {"code": "DDDDD"}],
    )
    @patch(
        "pretix_event_person_forwarder.forwarder.Questions.get_all_event_questions",
        return_value=DEST_QUESTIONS,
    )
    @patch(
        "pretix_event_person_forwarder.forwarder.Orders.get_event_orders",
        side_effect=[
            [
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
            ],
            DEST_ORDERS_WITH_JANE,
        ],
    )
    def test_no_email_attendee_is_always_posted(self, mock_orders, mock_questions, mock_api):
        rules_no_questions = {
            "fields": {
                "attendee_name": "attendee_name",
                "attendee_email": "attendee_email",
                "questions": [],
            }
        }
        forwarder = Forwarder(SOURCE_MODEL, DEST_MODEL, rules_no_questions, "update")
        forwarder.forward_event_persons("src-org", "src-event", "dst-org", "dst-event")
        self.assertEqual(mock_api.call_count, 2)
        post_call = mock_api.call_args_list[1]
        path_arg = post_call[0][0]
        self.assertNotIn("BBBBB", path_arg)
        self.assertNotIn("positions", path_arg)

    @patch(
        "pretix_event_person_forwarder.forwarder.Api.call_the_api",
        side_effect=[DEST_ITEMS, {}],
    )
    @patch(
        "pretix_event_person_forwarder.forwarder.Questions.get_all_event_questions",
        return_value=DEST_QUESTIONS,
    )
    @patch(
        "pretix_event_person_forwarder.forwarder.Orders.get_event_orders",
        side_effect=[
            [
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
            ],
            DEST_ORDERS_WITH_DUPLICATE_EMAIL,
        ],
    )
    def test_duplicate_email_uses_latest_position(self, mock_orders, mock_questions, mock_api):
        forwarder = Forwarder(SOURCE_MODEL, DEST_MODEL, RULES, "update")
        forwarder.forward_event_persons("src-org", "src-event", "dst-org", "dst-event")
        self.assertEqual(mock_api.call_count, 2)
        patch_call = mock_api.call_args_list[1]
        path_arg = patch_call[0][0]
        self.assertIn("11", path_arg)

    @patch(
        "pretix_event_person_forwarder.forwarder.Api.call_the_api",
        side_effect=[DEST_ITEMS, {"code": "CCCCC"}],
    )
    @patch(
        "pretix_event_person_forwarder.forwarder.Questions.get_all_event_questions",
        return_value=DEST_QUESTIONS,
    )
    @patch(
        "pretix_event_person_forwarder.forwarder.Orders.get_event_orders",
        side_effect=[
            [
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
            ],
            DEST_ORDERS_WITH_NO_EMAIL,
        ],
    )
    def test_destination_position_without_email_is_ignored(self, mock_orders, mock_questions, mock_api):
        forwarder = Forwarder(SOURCE_MODEL, DEST_MODEL, RULES, "update")
        forwarder.forward_event_persons("src-org", "src-event", "dst-org", "dst-event")
        self.assertEqual(mock_api.call_count, 2)
        post_call = mock_api.call_args_list[1]
        posted = json.loads(post_call[1]["json_complete"])
        self.assertEqual(posted["positions"][0]["attendee_email"], "jane@example.com")
