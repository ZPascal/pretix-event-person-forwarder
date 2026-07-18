import os
from unittest import TestCase

from tests.integrationtest.conftest import create_api_model_with_ssl
from pretix_event_person_forwarder.questions import Questions

HOST = os.environ.get("PRETIX_HOST", "https://localhost")
TOKEN = os.environ.get("PRETIX_TOKEN", "")
CA_BUNDLE = os.environ.get("PRETIX_CA_BUNDLE", None)


class QuestionsIntegrationTest(TestCase):
    def setUp(self):
        self.api_model = create_api_model_with_ssl(HOST, TOKEN, CA_BUNDLE)
        self.questions = Questions(self.api_model)

    def test_get_all_event_questions(self):
        result = self.questions.get_all_event_questions("dpsg-speyer", "prisma-2025")

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
