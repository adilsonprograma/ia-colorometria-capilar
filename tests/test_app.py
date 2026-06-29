import json
from http.client import HTTPConnection
import threading
import unittest

from app import create_server


class AppServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = create_server("127.0.0.1", 0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def make_request(
        self,
        method: str,
        path: str,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, dict[str, str], bytes]:
        connection = HTTPConnection("127.0.0.1", self.port, timeout=5)

        try:
            connection.request(method, path, body=body, headers=headers or {})
            response = connection.getresponse()
            payload = response.read()
            response_headers = {key: value for key, value in response.getheaders()}
            return response.status, response_headers, payload
        finally:
            connection.close()

    def test_root_route_serves_html(self) -> None:
        status, headers, payload = self.make_request("GET", "/")

        self.assertEqual(status, 200)
        self.assertIn("text/html", headers.get("Content-Type", ""))
        self.assertIn("ColorIA", payload.decode("utf-8"))

    def test_health_endpoint_returns_json(self) -> None:
        status, headers, payload = self.make_request("GET", "/api/health")
        data = json.loads(payload.decode("utf-8"))

        self.assertEqual(status, 200)
        self.assertEqual(headers.get("Access-Control-Allow-Origin"), "*")
        self.assertEqual(data["status"], "ok")
        self.assertIn("initialPrompt", data)

    def test_options_preflight_allows_json_chat_requests(self) -> None:
        status, headers, payload = self.make_request("OPTIONS", "/api/chat")

        self.assertEqual(status, 204)
        self.assertEqual(payload, b"")
        self.assertEqual(headers.get("Access-Control-Allow-Origin"), "*")
        self.assertIn("POST", headers.get("Access-Control-Allow-Methods", ""))

    def test_chat_endpoint_accepts_json_body(self) -> None:
        payload = json.dumps(
            {
                "message": "preto",
                "context": {"step": 0, "baseColor": "", "targetColor": ""},
            }
        ).encode("utf-8")

        status, headers, raw_response = self.make_request(
            "POST",
            "/api/chat",
            body=payload,
            headers={"Content-Type": "application/json"},
        )
        data = json.loads(raw_response.decode("utf-8"))

        self.assertEqual(status, 200)
        self.assertEqual(headers.get("Access-Control-Allow-Origin"), "*")
        self.assertEqual(data["context"]["step"], 1)
        self.assertIn("base atual e preto", data["response"])


if __name__ == "__main__":
    unittest.main()
