#!/usr/bin/env python3
"""Example dynamic-container challenge, served over TCP.

Each team gets its own container with a unique flag in the GZCTF_FLAG env
var (substituted from `flagTemplate` in challenge.yml). Read it once at
startup — unlike A&D, a jeopardy dynamic flag does not rotate.

Pure stdlib (socketserver) — no socat, no shell wrapper. Replace the
handle() body with your real challenge; the only wiring that matters is
"read GZCTF_FLAG and gate it behind your bug."
"""
import os
import socketserver

FLAG = os.environ.get("GZCTF_FLAG", "flag{local-test-flag}")
PORT = int(os.environ.get("PORT", "8011"))


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        # Toy "vulnerability": send the magic word, get the flag. Replace
        # this with something that actually has to be exploited.
        self.wfile.write(b"enter the magic word: ")
        self.wfile.flush()
        word = self.rfile.readline().strip()
        if word == b"sesame":
            self.wfile.write(FLAG.encode() + b"\n")
        else:
            self.wfile.write(b"access denied\n")


class Server(socketserver.ForkingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    Server(("0.0.0.0", PORT), Handler).serve_forever()
