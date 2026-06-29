from unittest import TestCase
from unittest.mock import patch

from pretix_event_person_forwarder.questions import Questions
from pretix_event_person_forwarder.model import APIModel

MODEL = APIModel(host="https://pretix.example.com/", token="test-token")

QUESTIONS_RESPONSE = {
    "counts": 1,
    "results": [{"id": 42, "question": {"en": "City"}}],
}
QUESTION_RESPONSE = {"id": 42, "question": {"en": "City"}}


class TestGetEventQuestion(TestCase):
    def test_returns_question_dict(self):
        with patch("pretix_event_person_forwarder.questions.Api.call_the_api", return_value=QUESTION_RESPONSE):
            result = Questions(MODEL).get_event_question("my-org", "my-event", 42)
        self.assertEqual(result, QUESTION_RESPONSE)

    def test_empty_organizer_raises_value_error(self):
        with self.assertRaises(ValueError):
            Questions(MODEL).get_event_question("", "my-event", 42)

    def test_empty_event_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            Questions(MODEL).get_event_question("my-org", "", 42)

    def test_zero_question_id_raises_value_error(self):
        with self.assertRaises(ValueError):
            Questions(MODEL).get_event_question("my-org", "my-event", 0)

    def test_api_error_empty_response_raises_exception(self):
        with patch("pretix_event_person_forwarder.questions.Api.call_the_api", return_value={}):
            with self.assertRaises(Exception):
                Questions(MODEL).get_event_question("my-org", "my-event", 42)


class TestGetAllEventQuestions(TestCase):
    def test_returns_results_list(self):
        with patch("pretix_event_person_forwarder.questions.Api.call_the_api", return_value=QUESTIONS_RESPONSE):
            result = Questions(MODEL).get_all_event_questions("my-org", "my-event")
        self.assertEqual(result, QUESTIONS_RESPONSE["results"])

    def test_empty_organizer_raises_value_error(self):
        with self.assertRaises(ValueError):
            Questions(MODEL).get_all_event_questions("", "my-event")

    def test_empty_event_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            Questions(MODEL).get_all_event_questions("my-org", "")

    def test_api_error_raises_exception(self):
        bad = {"counts": 0, "results": [{"id": None}]}
        with patch("pretix_event_person_forwarder.questions.Api.call_the_api", return_value=bad):
            with self.assertRaises(Exception):
                Questions(MODEL).get_all_event_questions("my-org", "my-event")
