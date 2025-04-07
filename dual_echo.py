from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading
import logging
import argparse
import signal
import sys

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
        self.wfile.write(b'{}')

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

def make_handler(status_code):
    return lambda *args, **kwargs: StaticResponseHandler(*args, status_code=status_code, **kwargs)

def start_server(port, status_code):
    server = ThreadedHTTPServer(("", port), make_handler(status_code))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    logging.info(f"Started server on port {port} with static response {status_code}")
    return server

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    server_200 = start_server(8080, 200)
    server_503 = start_server(8081, 503)

    def shutdown(*_):
        logging.info("Shutting down servers...")
        server_200.shutdown()
        server_503.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    signal.pause()  # Wait for signal

if __name__ == "__main__":
    main()
