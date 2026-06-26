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
