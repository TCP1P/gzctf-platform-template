#!/usr/bin/env python3
"""Toy King-of-the-Hill service — the "hill".

ONE shared container for the whole game. Teams compete to control it by
getting their platform-issued, per-round control token into the marker file
the platform reads:

    /koth/king

The platform contract is exactly that path: each tick it reads /koth/king from
this container, matches the bytes against the round token it issued to each
team, and credits the matching team hold points (while this service is also
functional — see ../checker). There is NO per-team flag in KotH.

The "take the hill" path below is a DELIBERATELY trivial unauthenticated write
(POST /king) so the template runs end-to-end. REPLACE it with your real
vulnerability — the whole challenge is making teams EARN the write to
/koth/king (an exploit, not a free POST). Keep the marker at /koth/king and
keep GET / working so the checker can tell the hill is alive.
"""
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# The platform reads THIS exact path each tick — don't move it.
KING_FILE = "/koth/king"
LISTEN_PORT = int(os.environ.get("PORT", "80"))

os.makedirs(os.path.dirname(KING_FILE), exist_ok=True)


def read_king() -> str:
    try:
        with open(KING_FILE) as f:
            return f.read().strip()
    except OSError:
        return ""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        king = read_king() or "(nobody)"
        body = f"king of the hill\ncurrent king token: {king}\n".encode()
        self._send(200, body)

    def do_POST(self):
        # TOY VULN — replace with your real exploit path. The point of a KotH
        # challenge is that planting your token in /koth/king must be HARD.
        if self.path != "/king":
            return self._send(404, b"not found\n")
        length = int(self.headers.get("Content-Length", "0") or "0")
        token = self.rfile.read(length).decode("utf-8", "replace").strip()
        if not token:
            return self._send(400, b"empty token\n")
        # Atomic write so the platform never reads a half-written marker.
        tmp = KING_FILE + ".tmp"
        with open(tmp, "w") as f:
            f.write(token)
        os.replace(tmp, KING_FILE)
        self._send(200, b"you are now king\n")

    def _send(self, code: int, body: bytes):
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass  # quiet — checker noise isn't useful in container logs


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", LISTEN_PORT), Handler).serve_forever()
