#!/usr/bin/env python3
"""
Example King of the Hill exploit.

KotH loop, run every round: fetch YOUR team's fresh control token from the
platform, then EXPLOIT the shared hill to write that token into /koth/king.
The platform reads /koth/king each tick — while it holds your token and the
hill is Ok, you score hold points. The token rotates every round, so you must
re-plant it (and fend off other teams overwriting the marker).

Get your Bearer token + the hill's address from the in-game Toolkit (the
per-game sidebar button: "Take the hill" / targets). KotH and A&D share one
API token.

    import requests

    base, game_id, chal_id, token = ...   # from the Toolkit

    # 1. fetch THIS round's control token (rotates every round)
    rt = requests.get(
        f"{base}/api/Game/{game_id}/Ad/Koth/{chal_id}/Token",
        headers={"Authorization": f"Bearer {token}"}, timeout=5,
    ).json()
    round_token = rt["token"]          # plant THIS exact string in /koth/king

    # 2. find the hill's ip:port (the KotH hill appears in the Targets list)
    targets = requests.get(
        f"{base}/api/Game/{game_id}/Ad/Targets",
        headers={"Authorization": f"Bearer {token}"}, timeout=5,
    ).json()
    # ... pick the hill matching chal_id -> ip, port ...

    # 3. EXPLOIT the hill to write the token into /koth/king. Here the toy bug
    #    is an open POST /king; your real target needs a real exploit (that's
    #    the challenge). The bytes you land in /koth/king must equal round_token.
    requests.post(f"http://{ip}:{port}/king", data=round_token, timeout=5)

    # 4. verify you're king, then re-run next round (the token will have rotated
    #    and rivals may have overwritten the marker).
    assert round_token in requests.get(f"http://{ip}:{port}/", timeout=5).text
"""
