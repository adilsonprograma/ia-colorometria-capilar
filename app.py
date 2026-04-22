from __future__ import annotations

import argparse
import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from chat_logic import ConversationState, INITIAL_PROMPT, process_input

PROJECT_ROOT = Path(__file__).resolve().parent
STATIC_ROUTES = {
    "/": "index.html",
    "/index.html": "index.html",
    "/style.css": "style.css",
    "/index.js": "index.js",
}


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


class ColorIARequestHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self) -> None:
        path = self._path()

        if path == "/favicon.ico":
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        if path == "/api/health":
            self._send_json(
                {
                    "status": "ok",
                    "appName": "ColorIA",
                    "initialPrompt": INITIAL_PROMPT,
                }
            )
            return

        static_file = STATIC_ROUTES.get(path)
        if static_file is not None:
            self._send_file(PROJECT_ROOT / static_file)
            return

        if path.startswith("/api/"):
            self._send_json({"error": "Rota da API nao encontrada."}, status=404)
            return

        self._send_text("Pagina nao encontrada.", status=404)

    def do_POST(self) -> None:
        path = self._path()
        if path != "/api/chat":
            self._send_json({"error": "Rota da API nao encontrada."}, status=404)
            return

        payload = self._read_json_body()
        if payload is None:
            return

        context_payload = payload.get("context")
        state = ConversationState.from_dict(
            context_payload if isinstance(context_payload, dict) else None
        )
        message = str(payload.get("message", "") or "").strip()

        if not message:
            self._send_json(
                {
                    "error": "A mensagem nao pode estar vazia.",
                    "context": state.to_dict(),
                },
                status=400,
            )
            return

        result = process_input(message, state)
        self._send_json(
            {
                "response": result.response,
                "context": result.state.to_dict(),
                "restart": result.restart,
            }
        )

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def log_message(self, format: str, *args: object) -> None:
        print(f"[{self.log_date_time_string()}] {self.address_string()} - {format % args}")

    def _path(self) -> str:
        return urlparse(self.path).path

    def _read_json_body(self) -> dict[str, object] | None:
        content_length_header = self.headers.get("Content-Length", "0")
        try:
            content_length = int(content_length_header)
        except ValueError:
            content_length = 0

        raw_body = self.rfile.read(content_length)

        try:
            decoded = raw_body.decode("utf-8") if raw_body else "{}"
            payload = json.loads(decoded)
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json({"error": "JSON invalido."}, status=400)
            return None

        if not isinstance(payload, dict):
            self._send_json({"error": "O corpo da requisicao deve ser um objeto JSON."}, status=400)
            return None

        return payload

    def _send_file(self, file_path: Path) -> None:
        if not file_path.exists():
            self._send_text("Arquivo nao encontrado.", status=404)
            return

        body = file_path.read_bytes()
        content_type, _ = mimetypes.guess_type(file_path.name)
        resolved_type = content_type or "application/octet-stream"

        if resolved_type.startswith("text/") or resolved_type in {
            "application/javascript",
            "application/json",
        }:
            resolved_type = f"{resolved_type}; charset=utf-8"

        self.send_response(200)
        self.send_header("Content-Type", resolved_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, message: str, status: int = 200) -> None:
        body = message.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: dict[str, object], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def create_server(host: str, port: int) -> ReusableThreadingHTTPServer:
    return ReusableThreadingHTTPServer((host, port), ColorIARequestHandler)


def parse_args() -> argparse.Namespace:
    default_host = os.environ.get("HOST", "0.0.0.0")

    try:
        default_port = int(os.environ.get("PORT", "8000"))
    except ValueError:
        default_port = 8000

    parser = argparse.ArgumentParser(description="Servidor local do ColorIA.")
    parser.add_argument("--host", default=default_host, help="Host para expor o servidor.")
    parser.add_argument("--port", type=int, default=default_port, help="Porta do servidor.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = create_server(args.host, args.port)
    print(f"ColorIA disponivel em http://{args.host}:{args.port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
