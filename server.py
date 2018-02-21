# python standard library
import argparse
from http.server import (
    HTTPServer,
    SimpleHTTPRequestHandler,
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Serve Sphinx")
    parser.add_argument(
        "--address", "-a", default="0.0.0.0",
        help="IP Address to serve the HTTP on (default=%(default)s)")
    parser.add_argument("--port", "-p", default=8000, type=int,
                        help="HTTP Port to use (default=%(default)s)")
    arguments = parser.parse_args()
    server = HTTPServer((arguments.address, arguments.port), SimpleHTTPRequestHandler)
    server.serve_forever()
