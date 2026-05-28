FROM python:3.12-alpine

# supervisor runs as PID 1 (see supervisord.conf) so the service runs as a child:
# it can crash or be restarted in place WITHOUT the container exiting, which lets
# an operator "restart" the box while keeping the team's filesystem changes
# (patches). Recreating the pod/container instead ("Reset") reverts to this
# image. Installed via pip so it reuses the image's existing python.
RUN pip install --no-cache-dir supervisor

# No baked flag. The platform supplies the live, rotating flag at the path in
# $GZCTF_FLAG_FILE (Docker: /flag bind-mount; Kubernetes: /gzctf-flag/flag,
# written by the flag-pull sidecar). ALWAYS read $GZCTF_FLAG_FILE — a service
# that hardcodes /flag works on Docker but serves a stale value on K8s. There
# is no GZCTF_FLAG env var for the service (it would freeze at start). Treat a
# missing file as "no flag yet" (warmup, before the first flag is planted).
COPY service.py /service.py
COPY supervisord.conf /etc/supervisord.conf

EXPOSE 80

# supervisord as PID 1; it runs service.py (pure stdlib http.server) as a child.
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
