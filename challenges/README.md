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
| [`king-of-the-hill/`](king-of-the-hill/) | `KingOfTheHill` | one SHARED hill; teams plant a per-round token in `/koth/king` to hold it (health-checked, no flag) |

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

## king-of-the-hill/

A King of the Hill challenge — one SHARED service every team fights to control:

```
king-of-the-hill/
├── challenge.yml     # type: KingOfTheHill + container (the hill) + ad (health checker)
├── src/              # the SHARED hill (platform auto-builds ./src/Dockerfile)
│   ├── Dockerfile    # exposes a writable marker at /koth/king; no flag
│   └── service.py    # toy hill — REPLACE the open POST /king with a real vuln
├── checker/          # HEALTH checker (no flag) — same harness as A&D
│   ├── Dockerfile
│   ├── checker.py    # harness (don't edit)
│   ├── checks.py     # ADD HEALTH CHECKS HERE (flag-free)
│   ├── run.py
│   └── requirements.txt
└── solver/
    └── solve.py      # fetch your round token, exploit the hill to plant it
```

**How KotH scores** — there is no flag. Each round the platform issues every
team a control token (`GET /api/Game/{id}/Ad/Koth/{cId}/Token`). A team's
exploit must land that token in the marker file `/koth/king` on the hill. Each
tick the platform reads `/koth/king`, matches it to the team it was issued to,
and — if the checker also says the hill is `Ok` — credits that team hold
points; holding a *broken* hill (checker not `Ok`) costs a penalty instead. The
token rotates every round, so teams must re-plant continually.

**The marker is `/koth/king`** — keep it at exactly that path: the platform
reads it from the container itself (you do NOT return it from the checker). The
`src/` toy hill ships an intentionally trivial `POST /king` write so it runs
out of the box — **replace it with your real vulnerability**; the whole
challenge is making the write to `/koth/king` something teams must earn.

**Checker is health-only** — KotH runs your checker with no flag, purely to
decide `Ok` / `Mumble` / `Offline` (which gates hold points vs penalty). Put
flag-free health assertions in `checker/checks.py` (don't reference `t.flag`).
Same harness + push rules as A&D. Omit `ad.checkerImage` for a TCP-reachability
probe.

**`allowSelfReset` must be false** — the hill is shared, so a team self-reset
would wipe everyone's progress. KotH wipes are governed by the game-level
refresh setting; that, hold-points-per-tick, and the leader cooldown are KotH
scoring knobs set in the admin UI after import (they aren't carried in the
`.gzevent` manifest — the shared `ad:` tick block does apply to KotH).
