# GZCTF Platform Template

Drop-in scaffolding for running a [GZCTF](https://github.com/GZTimeWalker/GZCTF) instance — pick docker-compose for a single-host VPS or k3s/Kubernetes for a multi-node cluster. Both paths land the same admin UI at `https://your.host/`.

Adapted from [gzcli's `ctf-template`](https://github.com/dimasma0305/gzcli/tree/main/internal/template/templates/others/ctf-template); k8s manifests added on top.

## Pick a path

| Path | Use when | Time-to-running |
|---|---|---|
| **[docker-compose](#docker-compose)** (`compose/` + `Makefile`) | Single VPS, you control the docker daemon, you want `gzcli sync` to manage challenges | ~2 minutes after edits |
| **[Kubernetes / k3s](#kubernetes--k3s)** (`k8s/`) | Multi-node cluster, you want native Pod isolation per challenge, you have an Ingress controller | ~5 minutes after edits |

## docker-compose

```sh
# 1. Seed your operator config (never commit this file)
cp compose/appsettings.example.json compose/appsettings.json
$EDITOR compose/.env              # WORKSPACE, PUBLIC_ENTRY, ACME email
$EDITOR compose/appsettings.json  # admin seed password + DB password + (optional) SMTP

# 2. Create the `traefik` docker network + start everything
make setup        # idempotent: creates the external `traefik` network
make platform-up  # gzctf + db + cache + traefik

# 3. After first boot, promote the seeded admin user
make init-admin   # runs UPDATE … SET Role=3 WHERE UserName='admin'
```

Run `make help` for the full target list. The most useful day-to-day:

| Target | What |
|---|---|
| `make platform-up` / `down` / `restart` | start, stop, or restart the whole stack |
| `make pull` | pull the latest image for every service |
| `make platform-clean` | stop + drop volumes (data loss) |
| `make {gzctf,db,cache,traefik}-logs` | tail one service |
| `make flush-cache` | wipe redis (scoreboard rebuilds on next request) |
| `make init-admin` | promote the seeded admin to Admin role |

Final layout under `compose/`:

```
compose/
├── .env                          # WORKSPACE / PUBLIC_ENTRY / ACME email
├── appsettings.example.json      # template — copy to appsettings.json before first up
├── compose.yml                   # main stack (gzctf, db, cache)
└── compose.traefik.yml           # traefik service definition + ACME settings
```

`appsettings.json` is in `.gitignore` — it carries DB + admin secrets and is per-deployment.

## Kubernetes / k3s

```sh
cd k8s/
$EDITOR 30-gzctf-config.yaml   # CHANGE passwords + PublicEntry
$EDITOR 50-ingress.yaml        # CHANGE hostname (must match PublicEntry)

kubectl apply -f 00-namespace.yaml
kubectl apply -f 10-postgres.yaml
kubectl apply -f 20-redis.yaml
kubectl apply -f 30-gzctf-config.yaml
kubectl apply -f 40-gzctf.yaml
kubectl apply -f 50-ingress.yaml

kubectl -n gzctf rollout status deploy/gzctf
```

See [`k8s/README.md`](k8s/README.md) for the full walk-through including:
- Storage class overrides for multi-node clusters
- RBAC scope (gzctf gets pod-create only inside `gzctf-challenges`)
- Switching from Traefik's ACME to cert-manager
- How honeypot ports work (and why they're omitted by default in the k8s path)

## After first boot

1. Open `https://<your-host>/` and log in as `admin` with the password from your config
2. Go to `/admin/repo-bindings` and point GZCTF at your challenges repo
3. Wait ~60 s for the first scan — games + challenges show up automatically

## Updating

```sh
# docker-compose
docker compose -f compose/compose.yml pull && make platform-up

# kubernetes
kubectl -n gzctf rollout restart deploy/gzctf
```

(Image tag is `gztime/gzctf:latest` in both paths; pin to a release tag in production.)

## What this template does NOT include

- A real TLS certificate — Traefik / cert-manager fetches one via ACME on first request
- Backup automation — see the GZCTF docs for `pg_dump` cron job examples
- Per-team rate limiting at the ingress — depends on your edge proxy
- Monitoring (Prometheus / Loki) — bring your own observability stack

## License

Same upstream license as gzcli (MIT). See the gzcli repo for the canonical license text.
