from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import json
import logging
import signal
import sys
import argparse
import threading
import re

class EchoHandler(BaseHTTPRequestHandler):
    def do_GET(self): self._respond()
    def do_POST(self): self._respond()
    def do_PUT(self): self._respond()
    def do_DELETE(self): self._respond()

    def _respond(self):
        logging.info(f"Received {self.command} request at {self.path}")

        content_length = int(self.headers.get('Content-Length', 0))
        request_body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else None

        if self.path == "/healthz":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            return

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

class StaticResponseHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, status_code=200, **kwargs):
        self._static_status = status_code
        super().__init__(*args, **kwargs)

    def do_GET(self): self._respond()
    def do_POST(self): self._respond()
    def do_PUT(self): self._respond()
    def do_DELETE(self): self._respond()

    def _respond(self):
        logging.info(f"[{self.server.server_port}] {self.command} {self.path}")
        self.send_response(self._static_status)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b"{}")

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    def __init__(self, server_address, RequestHandlerClass, timeout=30):
        super().__init__(server_address, RequestHandlerClass)
        self.timeout = timeout
        self.socket.settimeout(self.timeout)

def run_echo_server(port):
    server = ThreadedHTTPServer(("", port), EchoHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    logging.info(f"Started echo server on port {port}")
    return server

def run_static_server(port, status_code):
    handler = lambda *args, **kwargs: StaticResponseHandler(*args, status_code=status_code, **kwargs)
    server = ThreadedHTTPServer(("", port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    logging.info(f"Started static server on port {port} with status {status_code}")
    return server

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["echo", "static", "dual", "map"], required=True, help="Server mode")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to (for echo/static mode)")
    parser.add_argument("--status", type=int, default=200, help="Status code to return (for static mode)")
    parser.add_argument("--static-map", type=str, help="Comma-separated list of status_code:port or echo:port or path:port pairs")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    servers = []
    if args.mode == "echo":
        servers.append(run_echo_server(args.port))
    elif args.mode == "static":
        servers.append(run_static_server(args.port, args.status))
    elif args.mode == "dual":
        servers.append(run_static_server(8080, 200))
        servers.append(run_static_server(8081, 503))
    elif args.mode == "map":
        if not args.static_map:
            logging.error("--static-map must be provided when using --mode map")
            sys.exit(1)
        for entry in args.static_map.split(","):
            code, port = entry.strip().split(":")
            if code == "echo":
                servers.append(run_echo_server(int(port)))
            elif code == "path":
                servers.append(run_echo_server(int(port)))
            else:
                servers.append(run_static_server(int(port), int(code)))

    def shutdown(*_):
        logging.info("Shutting down servers...")
        for s in servers:
            s.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    signal.pause()

if __name__ == "__main__":
    main()
