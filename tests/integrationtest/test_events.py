import os
from unittest import TestCase

from tests.integrationtest.conftest import create_api_model_with_ssl
from pretix_event_person_forwarder.events import Events

HOST = os.environ.get("PRETIX_HOST", "https://localhost")
TOKEN = os.environ.get("PRETIX_TOKEN", "")
CA_BUNDLE = os.environ.get("PRETIX_CA_BUNDLE", None)


class EventsIntegrationTest(TestCase):
    def setUp(self):
        self.api_model = create_api_model_with_ssl(HOST, TOKEN, CA_BUNDLE)
        self.events = Events(self.api_model)

    def test_get_events(self):
        result = self.events.get_events("dpsg-speyer")

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
