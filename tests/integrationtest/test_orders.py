import os

from unittest import TestCase

from pretix_event_person_forwarder.model import (
    APIModel,
)
from pretix_event_person_forwarder.orders import Orders


class OrdersTest(TestCase):
    model: APIModel = APIModel(
        host=os.environ["PRETIX_HOST"],
        token=os.environ["PRETIX_TOKEN"],
        http2_support=False,
        timeout=30.0,
    )
    orders: Orders = Orders(model)

    def test_a_get_event_orders(self):
        self.assertIsNotNone(self.orders.get_event_orders("dpsg-speyer", "prisma-2025"))

    def test_b_get_all_orders(self):
        self.assertIsNotNone(self.orders.get_all_orders("dpsg-speyer"))