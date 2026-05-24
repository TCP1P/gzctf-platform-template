#!/usr/bin/env python3
"""Toy vulnerable A&D service: echoes /flag over HTTP.

Replace this with your real service. The only platform contract is that
the round's flag lives at the GZCTF_FLAG_FILE path (default /flag) — the
platform rewrites it every tick. Read it fresh on each request so the
rotation is visible immediately (no caching).
"""
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

FLAG_FILE = os.environ.get("GZCTF_FLAG_FILE", "/flag")
LISTEN_PORT = int(os.environ.get("PORT", "80"))


def read_flag() -> str:
    try:
        with open(FLAG_FILE, "r") as f:
            return f.read().strip()
    except OSError:
        return "no flag yet"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = f"flag is: {read_flag()}\n".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass  # quiet — checker noise isn't useful in container logs


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", LISTEN_PORT), Handler).serve_forever()
