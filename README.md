# GZCTF platform template

Scaffolding to run a [GZCTF](https://github.com/GZTimeWalker/GZCTF) instance.

## Docker compose

```sh
$EDITOR compose/.env       # set PUBLIC_ENTRY
make setup                 # creates the external `traefik` docker network
make platform-up           # auto-generates appsettings.json + starts everything
make init-admin            # promotes the seeded `admin` user to Admin role
```

`make help` lists every target.

## Kubernetes / k3s

```sh
cd k8s/
$EDITOR 30-gzctf-config.yaml   # set passwords + PublicEntry
$EDITOR 50-ingress.yaml        # set hostname

kubectl apply -f .
kubectl -n gzctf rollout status deploy/gzctf
```

See [`k8s/README.md`](k8s/README.md) for details (storage classes, RBAC, cert-manager swap).
