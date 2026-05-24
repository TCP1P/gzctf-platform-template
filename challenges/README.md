# Challenge templates

Ready-to-edit scaffolds for authoring GZCTF challenges. Copy a folder,
edit it, then either:

- **`gzcli`** — push from this repo, or
- **Web upload** — zip the folder and drop it at
  `https://PUBLIC_ENTRY/games/<id>/submit` (the in-app submit page offers
  the same templates as one-click downloads).

The `value:` and any `visible:`/`enabled:` fields in `challenge.yml` are
ignored on import — points + visibility are admin-controlled after review.

## attack-defense/

A full Attack & Defense challenge:

```
attack-defense/
├── challenge.yml     # type: AttackDefense + container (service) + ad (checker/tick) blocks
├── src/              # the per-team SERVICE (platform auto-builds ./src/Dockerfile)
│   ├── Dockerfile    # serves /flag over HTTP; platform rotates /flag each tick
│   └── serve.sh
├── checker/          # SLA/correctness checker — build + push, then set ad.checkerImage
│   ├── Dockerfile
│   └── check.sh      # enochecker3 exit codes: 0 Ok / 1 Mumble / 2 Offline / 3 InternalError
└── solver/
    └── solve.py      # your attack exploit (run against other teams each tick)
```

**Flag flow** — you do NOT author flags for A&D. The platform plants a
fresh per-team flag into `/flag` inside every team's container at the
start of each tick (and exposes the first round's flag via the
`GZCTF_FLAG` env var). Your service must surface that flag through the
intended bug; the checker confirms it's retrievable; attackers steal it
from other teams and submit it via the API.

**Checker** — `ad.checkerImage` must be a *pushed* image reference
(local `./checker` paths are not auto-built for checkers yet). Leave it
empty to fall back to a plain TCP-reachability probe — services that
respond on their port score SLA `Ok`, silent ones score `Offline`, with
no flag-correctness (`Mumble`) distinction.

**Egress** — `ad.allowEgress: false` (default) sandboxes team containers
off the public internet. Flip to `true` only for services that genuinely
need an outbound call.
