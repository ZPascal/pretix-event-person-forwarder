import os

from unittest import TestCase

from pretix_event_person_forwarder.model import (
    APIModel,
)
from pretix_event_person_forwarder.events import Events


class EventsTest(TestCase):
    model: APIModel = APIModel(
        host=os.environ["PRETIX_HOST"],
        token=os.environ["PRETIX_TOKEN"],
        http2_support=False,
        timeout=30.0,
    )
    events: Events = Events(model)

    def test_a_get_events(self):
        self.assertIsNotNone((len(self.events.get_events("dpsg-speyer"))))

    def test_b_get_event(self):
        self.assertIsNotNone(self.events.get_event("dpsg-speyer", "prisma-2025"))