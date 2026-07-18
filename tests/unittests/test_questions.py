from unittest import TestCase
from unittest.mock import patch

from pretix_event_person_forwarder.model import APIModel
from pretix_event_person_forwarder.questions import Questions


class TestQuestionsGetEventQuestion(TestCase):
    def setUp(self):
        self.api_model = APIModel(host="https://example.com/", token="test-token")
        self.questions = Questions(self.api_model)

    @patch("pretix_event_person_forwarder.questions.Api.call_the_api")
    def test_get_event_question_success(self, mock_api):
        mock_api.return_value = {"id": 312, "question": {"en": "City"}, "required": False}

        result = self.questions.get_event_question("test-org", "test-event", 312)

        self.assertEqual(result["id"], 312)
        self.assertEqual(result["question"]["en"], "City")

    def test_get_event_question_missing_organizer(self):
        with self.assertRaises(ValueError):
            self.questions.get_event_question("", "test-event", 312)

    def test_get_event_question_missing_event(self):
        with self.assertRaises(ValueError):
            self.questions.get_event_question("test-org", "", 312)

    def test_get_event_question_missing_question_id(self):
        with self.assertRaises(ValueError):
            self.questions.get_event_question("test-org", "test-event", 0)

    @patch("pretix_event_person_forwarder.questions.Api.call_the_api", side_effect=Exception("API Error"))
    def test_get_event_question_api_error(self, mock_api):
        with self.assertRaises(Exception):
            self.questions.get_event_question("test-org", "test-event", 312)

    @patch("pretix_event_person_forwarder.questions.Api.call_the_api", return_value={})
    def test_get_event_question_invalid_response_empty(self, mock_api):
        with self.assertRaises(Exception):
            self.questions.get_event_question("test-org", "test-event", 312)

    @patch("pretix_event_person_forwarder.questions.Api.call_the_api")
    def test_get_event_question_invalid_response_no_id(self, mock_api):
        mock_api.return_value = {"id": 0, "question": {"en": "City"}}

        with self.assertRaises(Exception):
            self.questions.get_event_question("test-org", "test-event", 312)


class TestQuestionsGetAllEventQuestions(TestCase):
    def setUp(self):
        self.api_model = APIModel(host="https://example.com/", token="test-token")
        self.questions = Questions(self.api_model)

    @patch("pretix_event_person_forwarder.questions.Api.call_the_api")
    def test_get_all_event_questions_success(self, mock_api):
        mock_api.return_value = {
            "count": 2,
            "counts": 2,
            "results": [
                {"id": 312, "question": {"en": "City"}},
                {"id": 313, "question": {"en": "Country"}}
            ]
        }

        result = self.questions.get_all_event_questions("test-org", "test-event")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], 312)

    @patch("pretix_event_person_forwarder.questions.Api.call_the_api")
    def test_get_all_event_questions_empty(self, mock_api):
        mock_api.return_value = {"count": 0, "counts": 0, "results": []}

        result = self.questions.get_all_event_questions("test-org", "test-event")
        self.assertEqual(result, [])

    def test_get_all_event_questions_missing_organizer(self):
        with self.assertRaises(ValueError):
            self.questions.get_all_event_questions("", "test-event")

    def test_get_all_event_questions_missing_event(self):
        with self.assertRaises(ValueError):
            self.questions.get_all_event_questions("test-org", "")

    @patch("pretix_event_person_forwarder.questions.Api.call_the_api", side_effect=Exception("Connection Error"))
    def test_get_all_event_questions_api_error(self, mock_api):
        with self.assertRaises(Exception):
            self.questions.get_all_event_questions("test-org", "test-event")

    @patch("pretix_event_person_forwarder.questions.Api.call_the_api")
    def test_get_all_event_questions_invalid_response(self, mock_api):
        mock_api.return_value = {
            "count": 1,
            "counts": 1,
            "results": [{"id": None, "question": {"en": "City"}}]
        }

        with self.assertRaises(Exception):
            self.questions.get_all_event_questions("test-org", "test-event")
