"""
KotH HEALTH checks live here. Unlike A&D, King of the Hill has NO per-team
flag — the platform decides who is king by reading the marker file /koth/king
from the hill itself. This checker is therefore a pure HEALTH probe: it only
decides whether the hill is Ok / Mumble / Offline, which gates whether the
current king earns hold points (Ok) or takes the broken-hill penalty.

So: do NOT reference `t.flag` here (it is empty for KotH). Just verify the hill
is up and behaving. The harness (checker.py) runs every @check each tick and
reports the worst verdict.

Each check receives a Target:
  t.url           "http://<ip>:<port>"  (the shared hill)
  t.round         round number (int)
  t.get(path)     HTTP GET  — raises Offline for you if the hill is down
  t.post(path)    HTTP POST — same
  t.request(m, p) any method

Verdicts:
  return normally   → this check passed (Ok)
  raise Mumble(msg) → hill reachable but degraded/wrong
  (unreachable)     → Offline, raised for you by t.get / t.post
"""
from checker import Mumble, check


@check
def hill_is_up(t):
    """The hill must answer GET / with 200 — otherwise it's down for everyone."""
    r = t.get("/")
    if r.status_code != 200:
        raise Mumble(f"GET / returned {r.status_code}")


@check
def hill_reports_king_state(t):
    """Functional check: the hill exposes its current-king view (the part the
    platform's marker read depends on staying alive). Tweak for your service."""
    body = t.get("/").text
    if "king of the hill" not in body:
        raise Mumble(f"unexpected hill response: {body[:120]!r}")


# ---------------------------------------------------------------------------
# Add more HEALTH checks below — each is just a decorated function. Keep them
# flag-free (KotH has no flag); assert that the parts of the hill teams must
# exploit + the marker path are functioning, e.g.:
#
# @check
# def claim_endpoint_alive(t):
#     # the hill must still accept a (legitimate) claim, else nobody can be king
#     if t.post("/king", data="healthcheck").status_code not in (200, 400):
#         raise Mumble("claim endpoint broken — nobody could take the hill")
# ---------------------------------------------------------------------------
