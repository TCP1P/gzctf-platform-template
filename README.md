# GZCTF Platform Template

Drop-in scaffolding for running a [GZCTF](https://github.com/GZTimeWalker/GZCTF) instance — pick docker-compose for a single-host VPS or k3s/Kubernetes for a multi-node cluster. Both paths land the same admin UI at `https://your.host/`.

Adapted from [gzcli's `ctf-template`](https://github.com/dimasma0305/gzcli/tree/main/internal/template/templates/others/ctf-template); k8s manifests added on top.

## Pick a path

| Path | Use when | Time-to-running |
|---|---|---|
| **[docker-compose](#docker-compose)** (`.gzctf/` + `Makefile`) | Single VPS, you control the docker daemon, you want `gzcli sync` to manage challenges | ~2 minutes after edits |
| **[Kubernetes / k3s](#kubernetes--k3s)** (`k8s/`) | Multi-node cluster, you want native Pod isolation per challenge, you have an Ingress controller | ~5 minutes after edits |

## docker-compose

```sh
# 1. Edit the env + appsettings before first up
$EDITOR .gzctf/.env             # WORKSPACE, PUBLIC_ENTRY, ACME email
$EDITOR .gzctf/appsettings.json # admin password seed, optional SMTP

# 2. Create the shared `challenges` docker network (gzcli also uses it)
docker network create challenges
docker network create traefik

# 3. Bring everything up
make setup           # one-time: build the manager container
make platform-up     # gzctf + db + cache + traefik
```

The `Makefile` exposes:

| Target | Purpose |
|---|---|
| `make platform-up` / `platform-down` | start/stop gzctf + db + cache + traefik |
| `make gzcli-start` / `gzcli-stop` | optional gzcli watcher sidecar (auto-sync from a git repo) |
| `make sync` | one-shot import of every `challenge.yml` under the current working tree |
| `make watch` / `watch-stop` / `watch-status` | follow-mode of `sync` for active dev |

The full layout under `.gzctf/`:

```
.gzctf/
├── compose.yml             # primary stack (gzctf, postgres, redis, traefik, challenges net)
├── compose.gzcli.yml       # overlay: gzcli sync container
├── compose.traefik.yml     # overlay: traefik + ACME settings
├── compose.upload.yml      # overlay: image upload tweaks
├── .env                    # WORKSPACE / PUBLIC_ENTRY / ACME email
├── appsettings.json        # gzctf platform config
├── conf.yaml               # gzcli config (linked from same hostname / token)
├── init_admin.sh           # bootstraps the first admin user
├── expose_docker.sh        # helper for exposing docker.sock to gzctf securely
├── manager/                # sidecar container that runs gzcli + cron jobs
└── *.schema.yaml           # YAML-LSP schemas for challenge.yml + .gzevent
```

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
docker compose -f .gzctf/compose.yml pull && make platform-up

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
