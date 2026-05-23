# GZCTF platform template

Scaffolding to run a [GZCTF](https://github.com/GZTimeWalker/GZCTF) instance.

## Docker compose

```sh
make wizard         # interactive prompts → writes .env + appsettings.json
make setup          # creates the external `traefik` docker network
make platform-up    # starts gzctf + db + cache + traefik
```

The wizard prints the auto-generated admin password at the end — copy
it before closing the terminal. Then log in at `https://PUBLIC_ENTRY`
as user `Admin`.

`make help` lists every target. SMTP / captcha / private-registry
credentials can also be configured later under `/admin/settings`.

## Kubernetes / k3s

```sh
cd k8s/
$EDITOR 30-gzctf-config.yaml   # set passwords + PublicEntry
$EDITOR 50-ingress.yaml        # set hostname

kubectl apply -f .
kubectl -n gzctf rollout status deploy/gzctf
```

See [`k8s/README.md`](k8s/README.md) for details (storage classes, RBAC, cert-manager swap).
