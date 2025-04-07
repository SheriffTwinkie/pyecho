from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import json
import logging
import signal
import sys
import argparse
import re

class EchoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._respond()

    def do_POST(self):
        self._respond()

    def do_PUT(self):
        self._respond()

    def do_DELETE(self):
        self._respond()

    def _respond(self):
        logging.info(f"Received {self.command} request at {self.path}")

        # Read request body if applicable
        content_length = int(self.headers.get('Content-Length', 0))
        request_body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else None

        # Handle health check
        if self.path == "/healthz":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            return

        # Handle /status/:code pattern
        status_match = re.match(r"^/status/(\d{3})$", self.path)
        if status_match:
            status_code = int(status_match.group(1))
            error_messages = {
                500: "Internal Server Error",
                502: "Bad Gateway",
                503: "Service Unavailable"
            }
            message = error_messages.get(status_code, "Custom Error")
            self.send_response(status_code)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            body = json.dumps({"status": status_code, "error": message})
            try:
                self.wfile.write(body.encode("utf-8"))
            except BrokenPipeError:
                logging.warning("Client disconnected before response was fully sent.")
            return

        # Handle named error routes
        if self.path == "/bad-request":
            self.send_response(400)
            response_body = json.dumps({"error": "Bad request"})
        elif self.path == "/not-found":
            self.send_response(404)
            response_body = json.dumps({"error": "Not found"})
        else:
            self.send_response(200)
            response_body = json.dumps({
                "message": "Hey! You hit the python!",
                "method": self.command,
                "path": self.path,
                "headers": dict(self.headers),
                "body": request_body,
            })

        self.send_header("Content-type", "application/json")
        self.end_headers()

        try:
            self.wfile.write(response_body.encode("utf-8"))
        except BrokenPipeError:
            logging.warning("Client disconnected before response was fully sent.")

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, timeout=30):
        super().__init__(server_address, RequestHandlerClass)
        self.timeout = timeout
        self.socket.settimeout(self.timeout)

def run(server_class=ThreadedHTTPServer, handler_class=EchoHandler, port=8080):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)

    def graceful_shutdown(signum, frame):
        logging.info("Shutting down gracefully...")
        httpd.shutdown()
        httpd.server_close()
        sys.exit(0)

    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    logging.info(f"Starting echo service on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        graceful_shutdown(None, None)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-level", type=str, default="INFO", help="Logging level")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s - %(message)s"
    )

    run(port=args.port)

if __name__ == "__main__":
    main()
