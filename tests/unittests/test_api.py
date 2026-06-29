import json
from unittest import TestCase
from unittest.mock import MagicMock, AsyncMock, patch

import httpx

from pretix_event_person_forwarder.api import Api
from pretix_event_person_forwarder.model import APIModel, RequestsMethods

MODEL = APIModel(host="https://pretix.example.com/", token="test-token")
MODEL_HTTP2 = APIModel(host="https://pretix.example.com/", token="test-token", http2_support=True)
MODEL_BASIC = APIModel(
    host="https://pretix.example.com/", username="user", password="pass"
)
MODEL_HEADERS = APIModel(
    host="https://pretix.example.com/", token="tok", headers={"X-Custom": "value"}
)


def _fake_response(body: any, status_code: int = 200) -> MagicMock:
    r = MagicMock()
    r.text = json.dumps(body)
    r.status_code = status_code
    return r


class TestCheckIfValidJson(TestCase):
    def test_valid_json_object(self):
        self.assertTrue(Api._check_if_valid_json('{"key": "value"}'))

    def test_valid_json_list(self):
        self.assertTrue(Api._check_if_valid_json('[1, 2, 3]'))

    def test_empty_string_json(self):
        # The implementation blocks b'""\n' (response body with trailing newline)
        self.assertFalse(Api._check_if_valid_json('""\n'))

    def test_null_json(self):
        self.assertFalse(Api._check_if_valid_json("null"))

    def test_plain_string_is_invalid(self):
        self.assertFalse(Api._check_if_valid_json("not json"))

    def test_empty_invalid(self):
        self.assertFalse(Api._check_if_valid_json(""))


class TestCheckApiCallResponse(TestCase):
    def test_returns_json_dict(self):
        r = _fake_response({"results": []})
        result = Api._check_the_api_call_response(r)
        self.assertEqual(result, {"results": []})

    def test_returns_json_list(self):
        r = _fake_response([{"id": 1}])
        result = Api._check_the_api_call_response(r)
        self.assertEqual(result, [{"id": 1}])

    def test_status_code_appended_to_dict(self):
        r = _fake_response({"key": "val"}, status_code=201)
        result = Api._check_the_api_call_response(r, response_status_code=True)
        self.assertEqual(result["status"], 201)

    def test_status_code_appended_to_list(self):
        r = _fake_response([{"id": 1}], status_code=200)
        result = Api._check_the_api_call_response(r, response_status_code=True)
        self.assertEqual(result[0]["status"], 200)

    def test_error_message_raises_connect_error(self):
        r = _fake_response({"message": "Invalid API key"})
        from httpx import ConnectError
        with self.assertRaises(ConnectError):
            Api._check_the_api_call_response(r)

    def test_non_json_response_returns_response_object(self):
        r = MagicMock()
        r.text = "not-json"
        r.status_code = 200
        result = Api._check_the_api_call_response(r)
        self.assertIs(result, r)

    def test_non_json_with_status_code_returns_dict(self):
        r = MagicMock()
        r.text = "plain text"
        r.status_code = 204
        result = Api._check_the_api_call_response(r, response_status_code=True)
        self.assertEqual(result["status"], 204)
        self.assertEqual(result["data"], "plain text")


class TestPrepareApiString(TestCase):
    def test_non_empty_appends_ampersand(self):
        self.assertEqual(Api.prepare_api_string("foo=bar"), "foo=bar&")

    def test_empty_returns_empty(self):
        self.assertEqual(Api.prepare_api_string(""), "")


class TestCreateHttpApiClient(TestCase):
    def test_sync_client_returned_for_http1(self):
        client = Api(MODEL).create_the_http_api_client({"Authorization": "Token t"})
        self.assertIsInstance(client, httpx.Client)

    def test_async_client_returned_for_http2(self):
        client = Api(MODEL_HTTP2).create_the_http_api_client({"Authorization": "Token t"})
        self.assertIsInstance(client, httpx.AsyncClient)


class TestCallTheApiSync(TestCase):
    def _api(self, model=MODEL):
        return Api(model)

    def _mock_client(self, response_body):
        mock = MagicMock()
        mock.__enter__ = MagicMock(return_value=mock)
        mock.__exit__ = MagicMock(return_value=False)
        mock.request = MagicMock(return_value=_fake_response(response_body))
        return mock

    def test_get_request(self):
        with patch.object(Api, "create_the_http_api_client", return_value=self._mock_client({"results": []})):
            result = self._api().call_the_api("api/v1/test/")
        self.assertEqual(result, {"results": []})

    def test_post_request(self):
        client = self._mock_client({"code": "ABC"})
        with patch.object(Api, "create_the_http_api_client", return_value=client):
            result = self._api().call_the_api(
                "api/v1/test/", method=RequestsMethods.POST, json_complete='{"name":"x"}'
            )
        self.assertEqual(result, {"code": "ABC"})

    def test_put_request(self):
        client = self._mock_client({"id": 1})
        with patch.object(Api, "create_the_http_api_client", return_value=client):
            result = self._api().call_the_api(
                "api/v1/test/1/", method=RequestsMethods.PUT, json_complete='{"name":"y"}'
            )
        self.assertEqual(result, {"id": 1})

    def test_patch_request(self):
        client = self._mock_client({"id": 1})
        with patch.object(Api, "create_the_http_api_client", return_value=client):
            result = self._api().call_the_api(
                "api/v1/test/1/", method=RequestsMethods.PATCH, json_complete='{"name":"z"}'
            )
        self.assertEqual(result, {"id": 1})

    def test_delete_request(self):
        client = self._mock_client({})
        with patch.object(Api, "create_the_http_api_client", return_value=client):
            result = self._api().call_the_api(
                "api/v1/test/1/", method=RequestsMethods.DELETE
            )
        self.assertEqual(result, {})

    def test_post_without_json_raises(self):
        client = self._mock_client({})
        with patch.object(Api, "create_the_http_api_client", return_value=client):
            with self.assertRaises(Exception):
                self._api().call_the_api("api/v1/test/", method=RequestsMethods.POST)

    def test_put_without_json_raises(self):
        client = self._mock_client({})
        with patch.object(Api, "create_the_http_api_client", return_value=client):
            with self.assertRaises(Exception):
                self._api().call_the_api("api/v1/test/", method=RequestsMethods.PUT)

    def test_patch_without_json_raises(self):
        client = self._mock_client({})
        with patch.object(Api, "create_the_http_api_client", return_value=client):
            with self.assertRaises(Exception):
                self._api().call_the_api("api/v1/test/", method=RequestsMethods.PATCH)

    def test_basic_auth_overrides_token(self):
        client = self._mock_client({"ok": True})
        with patch.object(Api, "create_the_http_api_client", return_value=client) as mock_create:
            Api(MODEL_BASIC).call_the_api("api/v1/test/")
            headers_used = mock_create.call_args[0][0]
            self.assertIn("Basic ", headers_used["Authorization"])

    def test_custom_headers_are_merged(self):
        client = self._mock_client({"ok": True})
        with patch.object(Api, "create_the_http_api_client", return_value=client) as mock_create:
            Api(MODEL_HEADERS).call_the_api("api/v1/test/")
            headers_used = mock_create.call_args[0][0]
            self.assertEqual(headers_used["X-Custom"], "value")

    def test_response_status_code_flag(self):
        client = self._mock_client({"data": "x"})
        with patch.object(Api, "create_the_http_api_client", return_value=client):
            result = self._api().call_the_api(
                "api/v1/test/", response_status_code=True
            )
        self.assertIn("status", result)

    def test_http2_path(self):
        response = _fake_response({"results": []})
        async_client = AsyncMock()
        async_client.request = AsyncMock(return_value=response)
        with patch.object(Api, "create_the_http_api_client", return_value=async_client):
            result = Api(MODEL_HTTP2).call_the_api("api/v1/test/")
        self.assertEqual(result, {"results": []})
