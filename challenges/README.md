# Challenge templates

Ready-to-edit scaffolds for authoring GZCTF challenges. Copy a folder,
edit it, then either:

- **`gzcli`** — push from this repo, or
- **Web upload** — zip the folder and drop it at
  `https://PUBLIC_ENTRY/games/<id>/submit` (the in-app submit page offers
  the same templates as one-click downloads).

The `value:` and any `visible:`/`enabled:` fields in `challenge.yml` are
ignored on import — points + visibility are admin-controlled after review.

### Stopping a challenge from syncing — `ignore: true`

Deleting a challenge in the admin UI removes it from the platform but **not**
from this repo, so a repo watch will re-import (resurrect) it on the next
sync. To keep it gone, add `ignore: true` to its `challenge.yml`:

```yaml
name: "old-challenge"
type: "StaticAttachment"
ignore: true   # importer skips this challenge entirely — never created/updated
```

`ignore: true` makes the importer skip the challenge (no create, no update),
so deleting it once in the UI sticks. It does **not** delete an
already-imported copy — remove that in the UI (or it just stops receiving
updates). Drop the key to start syncing again.

Three types are scaffolded here, matching the one-click templates on the
submit page:

| Folder | `type:` | Use for |
|---|---|---|
| [`static-attachment/`](static-attachment/) | `StaticAttachment` | files-only (crypto, reverse, forensics, misc) — no server |
| [`dynamic-container/`](dynamic-container/) | `DynamicContainer` | one container per team, unique flag via `GZCTF_FLAG` (pwn, web) |
| [`attack-defense/`](attack-defense/) | `AttackDefense` | persistent service + checker, flag rotates each tick |

Every folder follows the same layout: `challenge.yml` + `src/` (the
challenge, auto-built from `./src/Dockerfile` when it's a container) +
`solver/` (a working solver so reviewers can verify it). Put player
downloads in `dist/`.

## static-attachment/

```
static-attachment/
├── challenge.yml     # type: StaticAttachment + flags: + provide: ./dist
├── src/
│   └── flag.txt      # reference copy of the flag (NOT shipped to players)
├── dist/             # files players download (the binary, ciphertext, pcap…)
└── solver/
    └── solve.py      # how to recover the flag from ./dist
```

No container, no build. Players download whatever is in `dist/`; the flag
is matched server-side from the `flags:` list. Same static flag for every
team.

## dynamic-container/

```
dynamic-container/
├── challenge.yml     # type: DynamicContainer + container.flagTemplate/exposePort
├── src/
│   ├── Dockerfile    # platform auto-builds this
│   └── challenge.py  # pure-Python TCP service (socketserver), reads GZCTF_FLAG
├── dist/             # optional: hand players the source/binary
└── solver/
    └── solve.py      # connects + exploits + reads the flag
```

One container per team. The platform substitutes `[TEAM_HASH]` in
`flagTemplate` to give each team a unique flag and injects it as the
`GZCTF_FLAG` env var at container start — so a leaked flag identifies the
team it came from. The flag is fixed for the life of the container (it
does not rotate; that's A&D). Example service is stdlib `socketserver` —
no socat / shell wrapper.

## attack-defense/

A full Attack & Defense challenge:

```
attack-defense/
├── challenge.yml     # type: AttackDefense + container (service) + ad (checker) blocks
├── src/              # the per-team SERVICE (platform auto-builds ./src/Dockerfile)
│   ├── Dockerfile    # serves /flag over HTTP; platform rotates /flag each tick
│   └── service.py    # the toy vulnerable service (Python http.server)
├── checker/          # SLA/correctness checker — build + push, then set ad.checkerImage
│   ├── Dockerfile
│   ├── checker.py    # harness (don't edit) — registry + enochecker3 exit codes
│   ├── checks.py     # ADD YOUR TEST CASES HERE: a @check function each
│   ├── run.py        # entrypoint (imports checks, runs the harness)
│   └── requirements.txt
└── solver/
    └── solve.py      # your attack exploit (run against other teams each tick)
```

**Adding a checker test case** — edit `checker/checks.py`: write a
function that takes a `Target` and decorate it with `@check`. Return
normally to pass, `raise Mumble("why")` if the service is up but wrong;
`t.get(path)` / `t.post(path)` raise `Offline` for you if it's
unreachable. The harness runs every registered check each tick and
reports the worst verdict. No need to touch `checker.py` or `run.py`.

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

**Event-wide settings** — tick length, flag lifetime, reset cooldown, and
snapshot-download are **game** settings (admin → game → Info), not
per-challenge. A round spans the whole game, so every A&D service shares
one tick. The challenge `ad:` block only carries the service's own
properties (`checkerImage`, `allowEgress`, `allowSelfReset`).
