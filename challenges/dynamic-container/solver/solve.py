#!/usr/bin/env python3
"""Reference solver for the dynamic-container challenge.

Connects to the team's instance and exploits the bug to read the flag.
Stdlib sockets only (swap in pwntools if you prefer). The platform shows
each team the host:port for their own instance.

    python3 solve.py <host> <port>
"""
import socket
import sys


def solve(host: str, port: int) -> str:
    with socket.create_connection((host, port), timeout=5) as s:
        s.recv(4096)                      # banner / prompt
        s.sendall(b"sesame\n")            # the "exploit"
        return s.recv(4096).decode(errors="replace").strip()


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8011
    print(solve(host, port))
