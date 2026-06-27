import os
from unittest import TestCase

from pretix_event_person_forwarder.model import APIModel
from pretix_event_person_forwarder.forwarder import Forwarder

HOST = os.environ.get("PRETIX_HOST", "http://localhost")
TOKEN = os.environ.get("PRETIX_TOKEN", "")

RULES = {
    "fields": {
        "attendee_name": "attendee_name",
        "attendee_email": "attendee_email",
        "questions": [],
    }
}


class ForwarderIntegrationTest(TestCase):
    source_model: APIModel = APIModel(
        host=HOST,
        token=TOKEN,
        http2_support=False,
        timeout=30.0,
    )
    dest_model: APIModel = APIModel(
        host=HOST,
        token=TOKEN,
        http2_support=False,
        timeout=30.0,
    )

    def test_a_forward_persons_skip_mode(self):
        forwarder = Forwarder(
            self.source_model, self.dest_model, RULES, "skip"
        )
        forwarder.forward_event_persons(
            "source-org",
            "source-event",
            "dest-org",
            "dest-event",
        )

    def test_b_forward_persons_update_mode(self):
        forwarder = Forwarder(
            self.source_model, self.dest_model, RULES, "update"
        )
        forwarder.forward_event_persons(
            "source-org",
            "source-event",
            "dest-org",
            "dest-event",
        )
