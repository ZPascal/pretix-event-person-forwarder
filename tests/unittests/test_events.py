from unittest import TestCase
from unittest.mock import patch

from pretix_event_person_forwarder.events import Events
from pretix_event_person_forwarder.model import APIModel

MODEL = APIModel(host="https://pretix.example.com/", token="test-token")

EVENTS_RESPONSE = {
    "counts": 1,
    "results": [{"name": {"en": "My Event"}, "slug": "my-event"}],
}
EVENT_RESPONSE = {"slug": "my-event"}


class TestGetEvents(TestCase):
    def test_returns_results_list(self):
        with patch("pretix_event_person_forwarder.events.Api.call_the_api", return_value=EVENTS_RESPONSE):
            result = Events(MODEL).get_events("my-org")
        self.assertEqual(result, EVENTS_RESPONSE["results"])

    def test_empty_organizer_raises_value_error(self):
        with self.assertRaises(ValueError):
            Events(MODEL).get_events("")

    def test_api_error_raises_exception(self):
        bad = {"counts": 0, "results": [{"name": None}]}
        with patch("pretix_event_person_forwarder.events.Api.call_the_api", return_value=bad):
            with self.assertRaises(Exception):
                Events(MODEL).get_events("my-org")


class TestGetEvent(TestCase):
    def test_returns_event_dict(self):
        with patch("pretix_event_person_forwarder.events.Api.call_the_api", return_value=EVENT_RESPONSE):
            result = Events(MODEL).get_event("my-org", "my-event")
        self.assertEqual(result, EVENT_RESPONSE)

    def test_empty_organizer_raises_value_error(self):
        with self.assertRaises(ValueError):
            Events(MODEL).get_event("", "my-event")

    def test_empty_event_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            Events(MODEL).get_event("my-org", "")

    def test_api_error_raises_exception(self):
        bad = {"name": {"en": "oops"}}
        with patch("pretix_event_person_forwarder.events.Api.call_the_api", return_value=bad):
            with self.assertRaises(Exception):
                Events(MODEL).get_event("my-org", "my-event")
