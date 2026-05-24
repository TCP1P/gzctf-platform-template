"""
YOUR test cases live here. Adding one is the whole point: write a
function, decorate it with @check, done. The harness (checker.py) runs
every registered check each tick and reports the worst verdict.

Each check receives a Target:
  t.url           "http://<ip>:<port>"
  t.flag          the flag the platform planted into the service THIS tick
  t.round         round number (int)
  t.team_id       team being checked
  t.get(path)     HTTP GET  — raises Offline for you if the service is down
  t.post(path)    HTTP POST — same
  t.request(m, p) any method

Verdicts:
  return normally   → this check passed (Ok)
  raise Mumble(msg) → service reachable but wrong
  (unreachable)     → Offline, raised for you by t.get / t.post
"""
from checker import Mumble, check


@check
def flag_is_served(t):
    """The flag the platform planted this tick must be retrievable."""
    body = t.get("/").text
    if t.flag and t.flag not in body:
        raise Mumble(f"flag not in response: {body[:120]!r}")


@check
def content_type_is_plaintext(t):
    """Example functional check — tweak or delete for your own service."""
    ctype = t.get("/").headers.get("Content-Type", "")
    if "text/plain" not in ctype:
        raise Mumble(f"unexpected Content-Type: {ctype!r}")


# ---------------------------------------------------------------------------
# Add more test cases below — each is just a decorated function.
#
# import requests  # at the top, if a check needs sessions/cookies
#
# @check
# def login_then_read_secret(t):
#     r = t.post("/login", json={"user": "checker", "pw": "hunter2"})
#     if r.status_code != 200:
#         raise Mumble(f"login returned {r.status_code}")
#     secret = t.get("/me").json().get("secret", "")
#     if t.flag and t.flag not in secret:
#         raise Mumble("flag not exposed where it should be after login")
#
# @check
# def health_endpoint(t):
#     if t.get("/healthz").status_code != 200:
#         raise Mumble("/healthz did not return 200")
# ---------------------------------------------------------------------------
