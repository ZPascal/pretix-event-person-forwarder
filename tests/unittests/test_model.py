import ssl
from unittest import TestCase

from pretix_event_person_forwarder.model import APIModel, APIEndpoints, RequestsMethods


class TestAPIModel(TestCase):
    def test_api_model_required_fields(self):
        model = APIModel(host="https://example.com/", token="test-token")

        self.assertEqual(model.host, "https://example.com/")
        self.assertEqual(model.token, "test-token")

    def test_api_model_defaults(self):
        model = APIModel(host="https://example.com/", token="test-token")

        self.assertIsNone(model.username)
        self.assertIsNone(model.password)
        self.assertIsNone(model.headers)
        self.assertEqual(model.timeout, 10.0)
        self.assertFalse(model.http2_support)
        self.assertEqual(model.num_pools, 10)
        self.assertEqual(model.retries, 10)
        self.assertTrue(model.follow_redirects)

    def test_api_model_custom_timeout(self):
        model = APIModel(host="https://example.com/", token="test-token", timeout=30.0)

        self.assertEqual(model.timeout, 30.0)

    def test_api_model_custom_headers(self):
        headers = {"X-Custom": "value"}
        model = APIModel(host="https://example.com/", token="test-token", headers=headers)

        self.assertEqual(model.headers, headers)

    def test_api_model_http2_support(self):
        model = APIModel(host="https://example.com/", token="test-token", http2_support=True)

        self.assertTrue(model.http2_support)

    def test_api_model_basic_auth(self):
        model = APIModel(host="https://example.com/", token="test-token", username="user", password="pass")

        self.assertEqual(model.username, "user")
        self.assertEqual(model.password, "pass")

    def test_api_model_custom_ssl_context(self):
        custom_ssl = ssl.create_default_context()
        model = APIModel(host="https://example.com/", token="test-token", ssl_context=custom_ssl)

        self.assertEqual(model.ssl_context, custom_ssl)

    def test_api_model_ssl_context_default(self):
        model = APIModel(host="https://example.com/", token="test-token")

        self.assertIsNotNone(model.ssl_context)
        self.assertIsInstance(model.ssl_context, ssl.SSLContext)

    def test_api_model_custom_retries(self):
        model = APIModel(host="https://example.com/", token="test-token", retries=5)

        self.assertEqual(model.retries, 5)

    def test_api_model_retries_false(self):
        model = APIModel(host="https://example.com/", token="test-token", retries=False)

        self.assertFalse(model.retries)

    def test_api_model_follow_redirects(self):
        model = APIModel(host="https://example.com/", token="test-token", follow_redirects=False)

        self.assertFalse(model.follow_redirects)


class TestAPIEndpoints(TestCase):
    def test_endpoints_organizers(self):
        self.assertEqual(APIEndpoints.ORGANIZERS.value, "/api/v1/organizers")

    def test_endpoints_events(self):
        self.assertEqual(APIEndpoints.EVENTS.value, "events")

    def test_endpoints_items(self):
        self.assertEqual(APIEndpoints.ITEMS.value, "items")

    def test_endpoints_orders(self):
        self.assertEqual(APIEndpoints.ORDERS.value, "orders")

    def test_endpoints_questions(self):
        self.assertEqual(APIEndpoints.QUESTIONS.value, "questions")

    def test_endpoints_api_version(self):
        self.assertEqual(APIEndpoints.version_1.value, "v1")


class TestRequestsMethods(TestCase):
    def test_methods_get(self):
        self.assertEqual(RequestsMethods.GET.value, "GET")

    def test_methods_post(self):
        self.assertEqual(RequestsMethods.POST.value, "POST")

    def test_methods_patch(self):
        self.assertEqual(RequestsMethods.PATCH.value, "PATCH")

    def test_methods_put(self):
        self.assertEqual(RequestsMethods.PUT.value, "PUT")

    def test_methods_delete(self):
        self.assertEqual(RequestsMethods.DELETE.value, "DELETE")
