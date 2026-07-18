import os
from unittest import TestCase

from tests.integrationtest.conftest import create_api_model_with_ssl
from pretix_event_person_forwarder.orders import Orders

HOST = os.environ.get("PRETIX_HOST", "https://localhost")
TOKEN = os.environ.get("PRETIX_TOKEN", "")
CA_BUNDLE = os.environ.get("PRETIX_CA_BUNDLE", None)


class OrdersIntegrationTest(TestCase):
    def setUp(self):
        self.api_model = create_api_model_with_ssl(HOST, TOKEN, CA_BUNDLE)
        self.orders = Orders(self.api_model)

    def test_get_event_orders(self):
        result = self.orders.get_event_orders("dpsg-speyer", "prisma-2025")

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_get_all_orders(self):
        result = self.orders.get_all_orders("dpsg-speyer")

        self.assertIsInstance(result, list)
