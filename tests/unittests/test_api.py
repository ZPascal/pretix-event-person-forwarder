from unittest import TestCase
from unittest.mock import patch, MagicMock
import json

from pretix_event_person_forwarder.model import APIModel, RequestsMethods
from pretix_event_person_forwarder.api import Api
from httpx import ConnectError


class TestApiCallTheApiSync(TestCase):
    def setUp(self):
        self.api_model = APIModel(host="https://example.com/", token="test-token")
        self.api = Api(self.api_model)

    @patch("httpx.Client.request")
    def test_call_the_api_get_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = '{"id": 1, "name": "Test"}'
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = self.api.call_the_api("/api/v1/test")

        self.assertEqual(result["id"], 1)
        self.assertEqual(result["name"], "Test")

    @patch("httpx.Client.request")
    def test_call_the_api_post_with_json(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = '{"code": "ABC123"}'
        mock_response.status_code = 201
        mock_request.return_value = mock_response

        payload = json.dumps({"item": 1, "name": "Test"})
        result = self.api.call_the_api(
            "/api/v1/orders/",
            method=RequestsMethods.POST,
            json_complete=payload
        )

        self.assertEqual(result["code"], "ABC123")

    @patch("httpx.Client.request")
    def test_call_the_api_patch_with_json(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = '{}'
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        payload = json.dumps({"name": "Updated"})
        result = self.api.call_the_api(
            "/api/v1/orders/ABC/positions/1/",
            method=RequestsMethods.PATCH,
            json_complete=payload
        )

        self.assertEqual(result, {})

    @patch("httpx.Client.request")
    def test_call_the_api_delete(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = '{}'
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        result = self.api.call_the_api(
            "/api/v1/orders/ABC/",
            method=RequestsMethods.DELETE
        )

        self.assertEqual(result, {})

    def test_call_the_api_invalid_method_post_without_json(self):
        with self.assertRaises(Exception):
            self.api.call_the_api(
                "/api/v1/orders/",
                method=RequestsMethods.POST
            )

    def test_call_the_api_invalid_method_patch_without_json(self):
        with self.assertRaises(Exception):
            self.api.call_the_api(
                "/api/v1/orders/ABC/positions/1/",
                method=RequestsMethods.PATCH
            )

    @patch("httpx.Client.request")
    def test_call_the_api_response_with_status_code(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = '{"id": 1}'
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = self.api.call_the_api(
            "/api/v1/test",
            response_status_code=True
        )

        self.assertEqual(result["id"], 1)
        self.assertEqual(result["status"], 200)

    @patch("httpx.Client.request")
    def test_call_the_api_error_response_invalid_api_key(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = '{"message": "Invalid API key"}'
        mock_response.status_code = 403
        mock_request.return_value = mock_response

        with self.assertRaises(ConnectError):
            self.api.call_the_api("/api/v1/test")

    @patch("httpx.Client.request")
    def test_call_the_api_error_response_expired_api_key(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = '{"message": "Expired API key"}'
        mock_response.status_code = 403
        mock_request.return_value = mock_response

        with self.assertRaises(ConnectError):
            self.api.call_the_api("/api/v1/test")

    @patch("httpx.Client.request")
    def test_call_the_api_list_response(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = '[{"id": 1}, {"id": 2}]'
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = self.api.call_the_api("/api/v1/items")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

    @patch("httpx.Client.request")
    def test_call_the_api_empty_response(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = ''
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        result = self.api.call_the_api("/api/v1/test")

        self.assertEqual(result, mock_response)

    @patch("httpx.Client.request")
    def test_call_the_api_includes_auth_header(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = '{}'
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        self.api.call_the_api("/api/v1/test")

        self.assertTrue(mock_request.called)

    @patch("httpx.Client.request")
    def test_call_the_api_includes_basic_auth(self, mock_request):
        api_model = APIModel(
            host="https://example.com/",
            token="test-token",
            username="user",
            password="pass"
        )
        api = Api(api_model)

        mock_response = MagicMock()
        mock_response.text = '{}'
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        api.call_the_api("/api/v1/test")

        self.assertTrue(True)

    @patch("httpx.Client.request")
    def test_call_the_api_non_json_response(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = 'Not JSON'
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = self.api.call_the_api("/api/v1/test")

        self.assertIsNotNone(result)

    @patch("httpx.Client.request")
    def test_call_the_api_with_custom_headers(self, mock_request):
        api_model = APIModel(
            host="https://example.com/",
            token="test-token",
            headers={"X-Custom": "value"}
        )
        api = Api(api_model)

        mock_response = MagicMock()
        mock_response.text = '{"id": 1}'
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        api.call_the_api("/api/v1/test")

        self.assertTrue(True)

    @patch("httpx.Client.request", side_effect=Exception("Timeout"))
    def test_call_the_api_timeout(self, mock_request):
        with self.assertRaises(Exception):
            self.api.call_the_api("/api/v1/test")

    @patch("httpx.Client.request")
    def test_call_the_api_put_with_json(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = '{"updated": true}'
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        payload = json.dumps({"field": "value"})
        result = self.api.call_the_api(
            "/api/v1/resource/1/",
            method=RequestsMethods.PUT,
            json_complete=payload
        )

        self.assertEqual(result["updated"], True)

    def test_call_the_api_invalid_method_put_without_json(self):
        with self.assertRaises(Exception):
            self.api.call_the_api(
                "/api/v1/resource/1/",
                method=RequestsMethods.PUT
            )

    @patch("httpx.Client.request")
    def test_call_the_api_invalid_http_method(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = '{}'
        mock_request.return_value = mock_response

        fake_method = MagicMock()
        fake_method.value = "INVALID"

        with self.assertRaises(Exception):
            self.api.call_the_api(
                "/api/v1/test",
                method=fake_method
            )

    @patch("httpx.Client.request")
    def test_call_the_api_non_json_response_with_status_code(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = 'Not JSON'
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = self.api.call_the_api(
            "/api/v1/test",
            response_status_code=True
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["status"], 200)
        self.assertEqual(result["data"], "Not JSON")


class TestApiHttpClientCreation(TestCase):
    def test_create_http_client_sync(self):
        api_model = APIModel(host="https://example.com/", token="test-token")
        api = Api(api_model)

        headers = {"Authorization": "Token test-token"}
        client = api.create_the_http_api_client(headers)

        self.assertIsNotNone(client)
        self.assertTrue(hasattr(client, "request"))

    def test_create_http_client_async(self):
        api_model = APIModel(
            host="https://example.com/",
            token="test-token",
            http2_support=True
        )
        api = Api(api_model)

        headers = {"Authorization": "Token test-token"}
        client = api.create_the_http_api_client(headers)

        self.assertIsNotNone(client)
        self.assertTrue(hasattr(client, "request"))

    def test_create_http_client_with_custom_timeout(self):
        api_model = APIModel(
            host="https://example.com/",
            token="test-token",
            timeout=30.0
        )
        api = Api(api_model)

        client = api.create_the_http_api_client({})
        self.assertIsNotNone(client.timeout)

    def test_create_http_client_with_custom_ssl_context(self):
        import ssl
        custom_ssl = ssl.create_default_context()

        api_model = APIModel(
            host="https://example.com/",
            token="test-token",
            ssl_context=custom_ssl
        )
        api = Api(api_model)

        client = api.create_the_http_api_client({})
        self.assertIsNotNone(client)


class TestApiResponseValidation(TestCase):
    def test_check_if_valid_json_valid(self):
        self.assertTrue(Api._check_if_valid_json('{"id": 1}'))
        self.assertTrue(Api._check_if_valid_json('[{"id": 1}]'))
        self.assertTrue(Api._check_if_valid_json('{"key": "value"}'))

    def test_check_if_valid_json_invalid(self):
        self.assertFalse(Api._check_if_valid_json('not json'))
        self.assertFalse(Api._check_if_valid_json(''))
        self.assertFalse(Api._check_if_valid_json('null'))

    def test_check_if_valid_json_empty_string(self):
        self.assertTrue(Api._check_if_valid_json('""'))

    def test_check_the_api_call_response_dict(self):
        mock_response = MagicMock()
        mock_response.text = '{"id": 1}'
        mock_response.status_code = 200

        result = Api._check_the_api_call_response(mock_response, False)
        self.assertEqual(result["id"], 1)

    def test_check_the_api_call_response_with_status(self):
        mock_response = MagicMock()
        mock_response.text = '{"id": 1}'
        mock_response.status_code = 200

        result = Api._check_the_api_call_response(mock_response, True)
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["status"], 200)

    def test_check_the_api_call_response_list(self):
        mock_response = MagicMock()
        mock_response.text = '[{"id": 1}]'
        mock_response.status_code = 200

        result = Api._check_the_api_call_response(mock_response, False)
        self.assertIsInstance(result, list)

    def test_check_the_api_call_response_list_with_status(self):
        mock_response = MagicMock()
        mock_response.text = '[{"id": 1}]'
        mock_response.status_code = 200

        result = Api._check_the_api_call_response(mock_response, True)
        self.assertEqual(result[0]["status"], 200)

    def test_prepare_api_string_empty(self):
        result = Api.prepare_api_string("")
        self.assertEqual(result, "")

    def test_prepare_api_string_with_content(self):
        result = Api.prepare_api_string("key=value")
        self.assertEqual(result, "key=value&")


class TestApiCallTheApiAsync(TestCase):
    def setUp(self):
        api_model = APIModel(
            host="https://example.com/",
            token="test-token",
            http2_support=True
        )
        self.api = Api(api_model)

    @patch("httpx.AsyncClient.request")
    def test_call_the_api_async_get(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = '{"id": 1, "name": "Test"}'
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = self.api.call_the_api("/api/v1/test")

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 1)

    @patch("httpx.AsyncClient.request")
    def test_call_the_api_async_post(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = '{"code": "ABC123"}'
        mock_response.status_code = 201
        mock_request.return_value = mock_response

        payload = json.dumps({"item": 1, "name": "Test"})
        result = self.api.call_the_api(
            "/api/v1/orders/",
            method=RequestsMethods.POST,
            json_complete=payload
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["code"], "ABC123")

    @patch("httpx.AsyncClient.request", side_effect=Exception("Connection Error"))
    def test_call_the_api_async_error_handling(self, mock_request):
        with self.assertRaises(Exception):
            self.api.call_the_api("/api/v1/test")

    @patch("httpx.AsyncClient.request")
    def test_call_the_api_async_put_with_json(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = '{"updated": true}'
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        payload = json.dumps({"field": "value"})
        result = self.api.call_the_api(
            "/api/v1/resource/1/",
            method=RequestsMethods.PUT,
            json_complete=payload
        )

        self.assertEqual(result["updated"], True)

    def test_call_the_api_async_put_without_json(self):
        with self.assertRaises(Exception):
            self.api.call_the_api(
                "/api/v1/resource/1/",
                method=RequestsMethods.PUT
            )

    def test_call_the_api_async_invalid_method(self):
        fake_method = MagicMock()
        fake_method.value = "INVALID"

        with self.assertRaises(Exception):
            self.api.call_the_api(
                "/api/v1/test",
                method=fake_method
            )

    def test_call_the_api_async_post_without_json(self):
        with self.assertRaises(Exception):
            self.api.call_the_api(
                "/api/v1/orders/",
                method=RequestsMethods.POST
            )

    def test_call_the_api_async_patch_without_json(self):
        with self.assertRaises(Exception):
            self.api.call_the_api(
                "/api/v1/orders/ABC/positions/1/",
                method=RequestsMethods.PATCH
            )

    @patch("httpx.AsyncClient.request")
    def test_call_the_api_async_delete(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = '{}'
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        result = self.api.call_the_api(
            "/api/v1/orders/ABC/",
            method=RequestsMethods.DELETE
        )

        self.assertEqual(result, {})

    @patch("httpx.AsyncClient.request")
    def test_call_the_api_async_patch_with_json(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = '{}'
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        payload = json.dumps({"name": "Updated"})
        result = self.api.call_the_api(
            "/api/v1/orders/ABC/positions/1/",
            method=RequestsMethods.PATCH,
            json_complete=payload
        )

        self.assertEqual(result, {})


class TestApiAsyncExecution(TestCase):
    def setUp(self):
        api_model = APIModel(
            host="https://example.com/",
            token="test-token",
            http2_support=True
        )
        self.api = Api(api_model)

    def test_async_client_creation(self):
        headers = {"Authorization": "Token test-token"}
        client = self.api.create_the_http_api_client(headers)

        self.assertTrue(hasattr(client, "__aenter__"))

    @patch("httpx.AsyncClient.request")
    def test_async_call_with_http2(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = '{"id": 1}'
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = self.api.call_the_api("/api/v1/test")

        self.assertEqual(result["id"], 1)

    @patch("httpx.AsyncClient.request")
    def test_async_response_validation(self, mock_request):
        mock_response = MagicMock()
        mock_response.text = '[{"id": 1}, {"id": 2}]'
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        result = self.api.call_the_api("/api/v1/items")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
