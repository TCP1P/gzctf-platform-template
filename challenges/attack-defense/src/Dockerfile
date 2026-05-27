FROM python:3.12-alpine

# No baked flag. The platform supplies the live, rotating flag at the path in
# $GZCTF_FLAG_FILE (Docker: /flag bind-mount; Kubernetes: /gzctf-flag/flag,
# written by the flag-pull sidecar). ALWAYS read $GZCTF_FLAG_FILE — a service
# that hardcodes /flag works on Docker but serves a stale value on K8s. There
# is no GZCTF_FLAG env var for the service (it would freeze at start). Treat a
# missing file as "no flag yet" (warmup, before the first flag is planted).
COPY service.py /service.py

EXPOSE 80

# Pure stdlib (http.server) — no pip install needed for the service.
CMD ["python3", "/service.py"]
