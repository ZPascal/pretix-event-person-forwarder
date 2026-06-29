from unittest import TestCase
from unittest.mock import patch

from pretix_event_person_forwarder.orders import Orders
from pretix_event_person_forwarder.model import APIModel

MODEL = APIModel(host="https://pretix.example.com/", token="test-token")

ORDERS_RESPONSE = {
    "counts": 1,
    "results": [{"code": "AAAAA", "event": "my-event", "positions": []}],
}


class TestGetEventOrders(TestCase):
    def test_returns_results_list(self):
        with patch("pretix_event_person_forwarder.orders.Api.call_the_api", return_value=ORDERS_RESPONSE):
            result = Orders(MODEL).get_event_orders("my-org", "my-event")
        self.assertEqual(result, ORDERS_RESPONSE["results"])

    def test_empty_organizer_raises_value_error(self):
        with self.assertRaises(ValueError):
            Orders(MODEL).get_event_orders("", "my-event")

    def test_empty_event_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            Orders(MODEL).get_event_orders("my-org", "")

    def test_api_error_raises_exception(self):
        bad = {"counts": 0, "results": [{"event": None}]}
        with patch("pretix_event_person_forwarder.orders.Api.call_the_api", return_value=bad):
            with self.assertRaises(Exception):
                Orders(MODEL).get_event_orders("my-org", "my-event")


class TestGetAllOrders(TestCase):
    def test_returns_results_list(self):
        with patch("pretix_event_person_forwarder.orders.Api.call_the_api", return_value=ORDERS_RESPONSE):
            result = Orders(MODEL).get_all_orders("my-org")
        self.assertEqual(result, ORDERS_RESPONSE["results"])

    def test_empty_organizer_raises_value_error(self):
        with self.assertRaises(ValueError):
            Orders(MODEL).get_all_orders("")

    def test_api_error_raises_exception(self):
        bad = {"counts": 0, "results": [{"event": None}]}
        with patch("pretix_event_person_forwarder.orders.Api.call_the_api", return_value=bad):
            with self.assertRaises(Exception):
                Orders(MODEL).get_all_orders("my-org")
