from unittest import TestCase
from unittest.mock import patch

from pretix_event_person_forwarder.model import APIModel
from pretix_event_person_forwarder.events import Events


class TestEventsGetEvents(TestCase):
    def setUp(self):
        self.api_model = APIModel(host="https://example.com/", token="test-token")
        self.events = Events(self.api_model)

    @patch("pretix_event_person_forwarder.events.Api.call_the_api")
    def test_get_events_success(self, mock_api):
        mock_api.return_value = {
            "count": 2,
            "counts": 2,
            "results": [{"name": {"en": "Event 1"}, "slug": "event1"}, {"name": {"en": "Event 2"}, "slug": "event2"}],
        }

        result = self.events.get_events("test-org")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["slug"], "event1")

    @patch("pretix_event_person_forwarder.events.Api.call_the_api")
    def test_get_events_empty(self, mock_api):
        mock_api.return_value = {"count": 0, "counts": 0, "results": []}

        result = self.events.get_events("test-org")
        self.assertEqual(result, [])

    def test_get_events_missing_organizer(self):
        with self.assertRaises(ValueError):
            self.events.get_events("")

    @patch("pretix_event_person_forwarder.events.Api.call_the_api", side_effect=Exception("API Error"))
    def test_get_events_api_error(self, mock_api):
        with self.assertRaises(Exception):
            self.events.get_events("test-org")

    @patch("pretix_event_person_forwarder.events.Api.call_the_api")
    def test_get_events_invalid_response_no_name(self, mock_api):
        mock_api.return_value = {"count": 1, "counts": 1, "results": [{"name": None, "slug": "event1"}]}

        with self.assertRaises(Exception):
            self.events.get_events("test-org")


class TestEventsGetEvent(TestCase):
    def setUp(self):
        self.api_model = APIModel(host="https://example.com/", token="test-token")
        self.events = Events(self.api_model)

    @patch("pretix_event_person_forwarder.events.Api.call_the_api")
    def test_get_event_success(self, mock_api):
        """Note: get_event() has a bug in the actual code - it queries /events/ instead of /events/{event_name}
        This test documents the current behavior even though it's incorrect."""
        mock_api.return_value = {"name": {"en": "Event 1"}, "slug": "event1"}

        result = self.events.get_event("test-org", "event1")

        self.assertEqual(result["slug"], "event1")

    def test_get_event_missing_organizer(self):
        with self.assertRaises(ValueError):
            self.events.get_event("", "event1")

    def test_get_event_missing_event_name(self):
        with self.assertRaises(ValueError):
            self.events.get_event("test-org", "")

    @patch("pretix_event_person_forwarder.events.Api.call_the_api", side_effect=Exception("API Error"))
    def test_get_event_api_error(self, mock_api):
        with self.assertRaises(Exception):
            self.events.get_event("test-org", "event1")

    @patch("pretix_event_person_forwarder.events.Api.call_the_api")
    def test_get_event_invalid_response(self, mock_api):
        """Response without name triggers the error condition in get_event()"""
        mock_api.return_value = {"slug": "event1"}

        with self.assertRaises(Exception):
            self.events.get_event("test-org", "event1")
