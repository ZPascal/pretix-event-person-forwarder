import os
from unittest import TestCase

from pretix_event_person_forwarder.model import APIModel
from pretix_event_person_forwarder.forwarder import Forwarder
from tests.integrationtest.conftest import create_api_model_with_ssl

HOST = os.environ.get("PRETIX_HOST", "https://localhost")
TOKEN = os.environ.get("PRETIX_TOKEN", "")
CA_BUNDLE = os.environ.get("PRETIX_CA_BUNDLE", None)

RULES = {
    "fields": {
        "attendee_name": "attendee_name",
        "attendee_email": "attendee_email",
        "questions": [],
    }
}


class ForwarderIntegrationTest(TestCase):
    def setUp(self):
        api_model = create_api_model_with_ssl(HOST, TOKEN, CA_BUNDLE)
        self.source_model: APIModel = api_model
        self.dest_model: APIModel = api_model

    def test_a_forward_persons_skip_mode(self):
        forwarder = Forwarder(
            self.source_model, self.dest_model, RULES, "skip"
        )
        forwarder.forward_event_persons(
            "dpsg-speyer",
            "source-event",
            "dpsg-speyer",
            "dest-event",
        )

    def test_b_forward_persons_update_mode(self):
        forwarder = Forwarder(
            self.source_model, self.dest_model, RULES, "update"
        )
        forwarder.forward_event_persons(
            "dpsg-speyer",
            "source-event",
            "dpsg-speyer",
            "dest-event",
        )
