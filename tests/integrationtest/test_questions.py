import os

from unittest import TestCase

from pretix_event_person_forwarder.model import (
    APIModel,
)
from pretix_event_person_forwarder.questions import Questions


class OrdersTest(TestCase):
    model: APIModel = APIModel(
        host=os.environ["PRETIX_HOST"],
        token=os.environ["PRETIX_TOKEN"],
        http2_support=False,
        timeout=30.0,
    )
    questions: Questions = Questions(model)

    def test_a_get_event_questions(self):
        self.assertIsNotNone(self.questions.get_all_event_questions("dpsg-speyer", "prisma-2025"))

    def test_b_get_event_question(self):
        self.assertIsNotNone(self.questions.get_event_question("dpsg-speyer", "prisma-2025", 256))