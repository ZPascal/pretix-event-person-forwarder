from unittest import TestCase
from unittest.mock import patch

from pretix_event_person_forwarder.model import APIModel
from pretix_event_person_forwarder.orders import Orders


class TestOrdersGetEventOrders(TestCase):
    def setUp(self):
        self.api_model = APIModel(host="https://example.com/", token="test-token")
        self.orders = Orders(self.api_model)

    @patch("pretix_event_person_forwarder.orders.Api.call_the_api")
    def test_get_event_orders_success(self, mock_api):
        mock_api.return_value = {
            "count": 1,
            "counts": 1,
            "results": [
                {
                    "code": "ABC123",
                    "event": "test-event",
                    "positions": [{"id": 1, "attendee_name": "Jane Doe", "attendee_email": "jane@example.com"}],
                }
            ],
        }

        result = self.orders.get_event_orders("test-org", "test-event")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["code"], "ABC123")
        mock_api.assert_called_once()

    @patch("pretix_event_person_forwarder.orders.Api.call_the_api")
    def test_get_event_orders_empty_results(self, mock_api):
        mock_api.return_value = {"count": 0, "counts": 0, "results": []}

        result = self.orders.get_event_orders("test-org", "test-event")

        self.assertEqual(result, [])

    def test_get_event_orders_missing_organizer(self):
        with self.assertRaises(ValueError):
            self.orders.get_event_orders("", "test-event")

    def test_get_event_orders_missing_event_name(self):
        with self.assertRaises(ValueError):
            self.orders.get_event_orders("test-org", "")

    @patch("pretix_event_person_forwarder.orders.Api.call_the_api", side_effect=Exception("API Error"))
    def test_get_event_orders_api_error(self, mock_api):
        with self.assertRaises(Exception):
            self.orders.get_event_orders("test-org", "test-event")

    @patch("pretix_event_person_forwarder.orders.Api.call_the_api")
    def test_get_event_orders_invalid_response(self, mock_api):
        """Test when API response has results but event is None (indicates error)"""
        mock_api.return_value = {"count": 1, "counts": 1, "results": [{"code": "ABC", "event": None}]}

        with self.assertRaises(Exception):
            self.orders.get_event_orders("test-org", "test-event")


class TestOrdersGetAllOrders(TestCase):
    def setUp(self):
        self.api_model = APIModel(host="https://example.com/", token="test-token")
        self.orders = Orders(self.api_model)

    @patch("pretix_event_person_forwarder.orders.Api.call_the_api")
    def test_get_all_orders_success(self, mock_api):
        mock_api.return_value = {
            "count": 2,
            "counts": 2,
            "results": [
                {"code": "ORD1", "event": "event1", "positions": []},
                {"code": "ORD2", "event": "event2", "positions": []},
            ],
        }

        result = self.orders.get_all_orders("test-org")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["code"], "ORD1")

    @patch("pretix_event_person_forwarder.orders.Api.call_the_api")
    def test_get_all_orders_empty(self, mock_api):
        mock_api.return_value = {"count": 0, "counts": 0, "results": []}

        result = self.orders.get_all_orders("test-org")
        self.assertEqual(result, [])

    def test_get_all_orders_missing_organizer(self):
        with self.assertRaises(ValueError):
            self.orders.get_all_orders("")

    @patch("pretix_event_person_forwarder.orders.Api.call_the_api", side_effect=Exception("Connection Error"))
    def test_get_all_orders_api_error(self, mock_api):
        with self.assertRaises(Exception):
            self.orders.get_all_orders("test-org")

    @patch("pretix_event_person_forwarder.orders.Api.call_the_api")
    def test_get_all_orders_invalid_response(self, mock_api):
        mock_api.return_value = {"count": 1, "counts": 1, "results": [{"code": "ABC", "event": None}]}

        with self.assertRaises(Exception):
            self.orders.get_all_orders("test-org")
