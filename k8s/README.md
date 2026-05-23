# Kubernetes / k3s deployment

Apply-in-order manifests for running GZCTF on k3s (or any other k8s
distribution). Mirrors the docker-compose path under `compose/` but
swaps the `ContainerProvider` to `Kubernetes` so challenge instances
spawn as pods inside the `gzctf-challenges` namespace instead of via
the host's docker socket.

## Quick start

```sh
# 1. Fill in secrets + hostname (or use the auto-generation snippet below)
$EDITOR 30-gzctf-config.yaml
$EDITOR 50-ingress.yaml

# 2. Apply in order
kubectl apply -f 00-namespace.yaml
kubectl apply -f 10-postgres.yaml
kubectl apply -f 20-redis.yaml
kubectl apply -f 30-gzctf-config.yaml
kubectl apply -f 40-gzctf.yaml
kubectl apply -f 50-ingress.yaml

# 3. Watch the gzctf pod come up
kubectl -n gzctf rollout status deploy/gzctf
```

### Auto-generating secrets

Easier than editing the YAML by hand — apply the namespace first, then
overwrite the `gzctf-secrets` Secret with freshly-generated values
before applying `30-gzctf-config.yaml`:

```sh
kubectl apply -f 00-namespace.yaml

kubectl -n gzctf create secret generic gzctf-secrets \
  --from-literal=postgres-password="$(openssl rand -hex 16)" \
  --from-literal=xor-key="$(openssl rand -hex 32)" \
  --from-literal=admin-password="$(openssl rand -hex 12)" \
  --from-literal=smtp-username="" \
  --from-literal=smtp-password=""

# Then continue with the rest:
kubectl apply -f 10-postgres.yaml -f 20-redis.yaml \
              -f 30-gzctf-config.yaml -f 40-gzctf.yaml -f 50-ingress.yaml
```

Read the admin password back when you need to log in:

```sh
kubectl -n gzctf get secret gzctf-secrets -o jsonpath='{.data.admin-password}' | base64 -d
```

> **Don't rotate `xor-key` after first boot** — gzctf uses it to
> encrypt repo-binding PATs + registry passwords at rest. Changing
> the key after data lands breaks every encrypted value in the DB.

GZCTF will be reachable at the hostname configured in `50-ingress.yaml`
once cert-manager (or Traefik's built-in ACME) issues a TLS cert.

## What's here

| File | Purpose |
|---|---|
| `00-namespace.yaml` | Two namespaces: `gzctf` (platform) + `gzctf-challenges` (where challenge pods land) |
| `10-postgres.yaml` | PVC + Deployment + Service for postgres 17 |
| `20-redis.yaml` | Deployment + Service for redis (cache) |
| `30-gzctf-config.yaml` | ConfigMap holding `appsettings.json` (Kubernetes provider mode) + Secret for db password + ServiceAccount with RBAC for spawning challenge pods |
| `40-gzctf.yaml` | PVC for `/app/files` + Deployment + Service for gzctf |
| `50-ingress.yaml` | Traefik ingress + TLS (cert-manager / built-in resolver) |

## Differences from the docker-compose path

| Concern | docker-compose (`compose/`) | kubernetes (`k8s/`) |
|---|---|---|
| Challenge spawning | host docker socket | in-cluster ServiceAccount → spawns Pods in `gzctf-challenges` ns |
| Public entry | Traefik container on host | Cluster Ingress |
| Persistence | named docker volumes | PVCs |
| `appsettings.json` | mounted file | ConfigMap |
| Honeypot ports (5432, 6379, etc.) | published on host | omitted (would conflict with cluster's own postgres/redis services if any) — re-add via NodePort if you want them |
| `gzcli sync` watcher | `compose.gzcli.yml` overlay | not in scope; run gzcli from a workstation or a sidecar CronJob if you need it |

## Sizing

The Deployments ship with conservative resource requests/limits
matching the docker-compose `deploy.resources` block. Bump
`spec.template.spec.containers[].resources` if your CTF has > 50
concurrent participants.

## Storage

PVCs default to the cluster's default `StorageClass`. On k3s that's
`local-path` (single-node, on-disk under `/var/lib/rancher/k3s/storage`).
For multi-node clusters set `spec.storageClassName` explicitly on
each PVC (e.g. `longhorn`, `ceph-rbd`, etc.).

## RBAC notes

`30-gzctf-config.yaml` grants gzctf's ServiceAccount these verbs in
the `gzctf-challenges` namespace only (NOT cluster-wide):
- `pods`, `services`, `configmaps`, `secrets`: full CRUD
- `events`: read

The platform never touches the `gzctf` namespace's own resources at
runtime — pod spawning is fully scoped to `gzctf-challenges`. If you
move the challenges namespace, also update the RBAC `namespace:`
field + the `KubernetesConfig.Namespace` setting in the ConfigMap.
